"""Injectable clock so time-dependent rules (overdue/abandoned) are testable."""
from datetime import UTC, datetime


def utcnow() -> datetime:
    """Current UTC time as a naive datetime (SQLite stores naive timestamps)."""
    return datetime.now(UTC).replace(tzinfo=None)


def get_now() -> datetime:
    """FastAPI dependency returning 'now'. Overridden in tests."""
    return utcnow()
