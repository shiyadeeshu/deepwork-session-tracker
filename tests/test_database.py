"""Database-level tests: constraints, cascade delete, migrations and seed data."""
import sqlite3
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import inspect, text
from sqlalchemy.exc import IntegrityError

from app.models import Interruption, WorkSession

ROOT = Path(__file__).resolve().parent.parent


def test_status_check_constraint(db_session):
    db_session.add(WorkSession(title="x", scheduled_duration=10, status="bogus"))
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_deleting_session_cascades_to_interruptions(db_session):
    ws = WorkSession(title="x", scheduled_duration=10)
    ws.interruptions.append(Interruption(reason="r"))
    db_session.add(ws)
    db_session.commit()

    # Raw SQL delete proves the DB-level ON DELETE CASCADE works (foreign_keys pragma on).
    db_session.execute(text("DELETE FROM sessions WHERE id = :id"), {"id": ws.id})
    db_session.commit()
    remaining = db_session.execute(text("SELECT COUNT(*) FROM interruptions")).scalar()
    assert remaining == 0


def test_interruption_requires_existing_session(db_session):
    db_session.add(Interruption(session_id=12345, reason="orphan"))
    with pytest.raises(IntegrityError):
        db_session.commit()


@pytest.fixture
def migrated_db(tmp_path):
    db_file = tmp_path / "migrated.db"
    cfg = Config(str(ROOT / "alembic.ini"))
    cfg.set_main_option("script_location", str(ROOT / "alembic"))
    cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_file}")
    command.upgrade(cfg, "head")
    return cfg, db_file


def test_alembic_upgrade_creates_schema(migrated_db):
    from sqlalchemy import create_engine

    _, db_file = migrated_db
    insp = inspect(create_engine(f"sqlite:///{db_file}"))
    assert {"sessions", "interruptions"} <= set(insp.get_table_names())
    cols = {c["name"] for c in insp.get_columns("sessions")}
    assert cols == {
        "id", "title", "goal", "scheduled_duration", "start_time", "end_time", "status", "created_at",
    }


def test_alembic_downgrade(migrated_db):
    cfg, db_file = migrated_db
    command.downgrade(cfg, "base")
    tables = {r[0] for r in sqlite3.connect(db_file).execute("SELECT name FROM sqlite_master")}
    assert "sessions" not in tables and "interruptions" not in tables


def test_seed_data_loads_and_matches_rules(migrated_db):
    _, db_file = migrated_db
    conn = sqlite3.connect(db_file)
    conn.executescript((ROOT / "seed_data.sql").read_text(encoding="utf-8"))
    statuses = {r[0] for r in conn.execute("SELECT status FROM sessions")}
    assert statuses == {
        "scheduled", "active", "paused", "completed", "interrupted", "abandoned", "overdue",
    }
    # the interrupted seed row really has > 3 pauses
    (pauses,) = conn.execute(
        "SELECT COUNT(*) FROM interruptions i JOIN sessions s ON s.id = i.session_id "
        "WHERE s.status = 'interrupted'"
    ).fetchone()
    assert pauses > 3
