"""Pydantic request/response models (these define the OpenAPI schema & SDK models)."""
from datetime import UTC, datetime
from typing import Annotated

from pydantic import AfterValidator, BaseModel, ConfigDict, Field

from app.models import SessionStatus


def _as_utc(value: datetime | None) -> datetime | None:
    # DB timestamps are naive UTC; tag them so clients don't read them as local time.
    if value is not None and value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value


UtcDatetime = Annotated[datetime, AfterValidator(_as_utc)]


# ---------- Requests ----------

class SessionCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(..., min_length=1, max_length=200, examples=["Write report intro"])
    goal: str | None = Field(None, max_length=1000, examples=["Finish the first draft"])
    scheduled_duration: int = Field(
        ..., gt=0, le=1440, description="Planned length in minutes", examples=[50]
    )


class PauseRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    reason: str = Field(..., min_length=1, max_length=500, examples=["Phone call"])


# ---------- Responses ----------

class InterruptionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reason: str
    pause_time: UtcDatetime


class SessionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    goal: str | None
    scheduled_duration: int = Field(description="Planned length in minutes")
    start_time: UtcDatetime | None
    end_time: UtcDatetime | None
    status: SessionStatus
    created_at: UtcDatetime
    pause_count: int
    interruptions: list[InterruptionRead]


class SessionHistoryItem(SessionRead):
    actual_duration_minutes: float | None = Field(
        description="Wall-clock minutes from start to end (pauses included)"
    )


class HistorySummary(BaseModel):
    total_sessions: int = Field(description="All sessions, any status")
    finished_sessions: int = Field(description="Sessions in a final state")
    status_counts: dict[SessionStatus, int]
    completion_ratio: float = Field(
        description="completed / finished sessions (0.0 when nothing has finished)"
    )
    total_pauses: int
    average_pauses_per_session: float
    total_focus_minutes: float = Field(description="Sum of actual durations of finished sessions")
    average_duration_minutes: float
    sessions: list[SessionHistoryItem] = Field(description="Finished sessions, newest first")


class ErrorResponse(BaseModel):
    detail: str
