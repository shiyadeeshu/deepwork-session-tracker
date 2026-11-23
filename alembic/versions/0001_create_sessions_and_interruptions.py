"""create sessions and interruptions tables

Revision ID: 0001
Revises:
Create Date: 2026-11-23
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

STATUSES = ("scheduled", "active", "paused", "completed", "interrupted", "abandoned", "overdue")


def upgrade() -> None:
    op.create_table(
        "sessions",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("title", sa.Text, nullable=False),
        sa.Column("goal", sa.Text),
        sa.Column("scheduled_duration", sa.Integer, nullable=False),
        sa.Column("start_time", sa.DateTime),
        sa.Column("end_time", sa.DateTime),
        sa.Column("status", sa.String, nullable=False, server_default="scheduled"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.current_timestamp()),
        sa.CheckConstraint(
            "status IN (" + ",".join(f"'{s}'" for s in STATUSES) + ")",
            name="ck_sessions_status",
        ),
        sqlite_autoincrement=True,
    )
    op.create_table(
        "interruptions",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "session_id",
            sa.Integer,
            sa.ForeignKey("sessions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("reason", sa.Text, nullable=False),
        sa.Column("pause_time", sa.DateTime, server_default=sa.func.current_timestamp()),
        sqlite_autoincrement=True,
    )
    op.create_index("ix_interruptions_session_id", "interruptions", ["session_id"])


def downgrade() -> None:
    op.drop_index("ix_interruptions_session_id", table_name="interruptions")
    op.drop_table("interruptions")
    op.drop_table("sessions")
