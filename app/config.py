"""Application settings, overridable via environment variables."""
import os

DATABASE_URL: str = os.getenv("DEEPWORK_DATABASE_URL", "sqlite:///./deepwork.db")

# Origins allowed to call the API from a browser (React dev servers).
CORS_ORIGINS: list[str] = os.getenv(
    "DEEPWORK_CORS_ORIGINS", "http://localhost:3000,http://localhost:5173"
).split(",")

# Business rules
MAX_PAUSES: int = 3  # pausing more than this many times -> interrupted
OVERDUE_TOLERANCE: float = 0.10  # must finish within +10% of scheduled duration
