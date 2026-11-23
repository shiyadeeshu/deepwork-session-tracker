"""Load seed_data.sql into the SQLite database (no sqlite3 CLI needed on Windows).

Usage:  python seed.py            (run `alembic upgrade head` first)
"""
import sqlite3
from pathlib import Path

from app.config import DATABASE_URL

ROOT = Path(__file__).parent


def main() -> None:
    if not DATABASE_URL.startswith("sqlite:///"):
        raise SystemExit("seed.py only supports SQLite file databases")
    db_path = DATABASE_URL.removeprefix("sqlite:///")
    sql = (ROOT / "seed_data.sql").read_text(encoding="utf-8")
    with sqlite3.connect(db_path) as conn:
        conn.executescript(sql)
    print(f"Seeded {db_path}")


if __name__ == "__main__":
    main()
