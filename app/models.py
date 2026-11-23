"""SQLAlchemy ORM models mirroring the required schema."""
import enum
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class SessionStatus(str, enum.Enum):
    scheduled = "scheduled"
    active = "active"
    paused = "paused"
    completed = "completed"
    interrupted = "interrupted"
    abandoned = "abandoned"
    overdue = "overdue"


TERMINAL_STATUSES = {
    SessionStatus.completed,
    SessionStatus.interrupted,
    SessionStatus.abandoned,
    SessionStatus.overdue,
}

_STATUS_VALUES = ",".join(f"'{s.value}'" for s in SessionStatus)


class WorkSession(Base):
    __tablename__ = "sessions"
    __table_args__ = (
        CheckConstraint(f"status IN ({_STATUS_VALUES})", name="ck_sessions_status"),
        {"sqlite_autoincrement": True},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    goal: Mapped[str | None] = mapped_column(Text)
    scheduled_duration: Mapped[int] = mapped_column(Integer, nullable=False)  # minutes
    start_time: Mapped[datetime | None] = mapped_column(DateTime)
    end_time: Mapped[datetime | None] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(
        String, nullable=False, default=SessionStatus.scheduled.value,
        server_default=SessionStatus.scheduled.value,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )

    interruptions: Mapped[list["Interruption"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="Interruption.id",
        lazy="selectin",
    )

    @property
    def pause_count(self) -> int:
        return len(self.interruptions)

    @property
    def actual_duration_minutes(self) -> float | None:
        """Wall-clock minutes from start to end (pauses included)."""
        if self.start_time is None or self.end_time is None:
            return None
        return round((self.end_time - self.start_time).total_seconds() / 60, 2)


class Interruption(Base):
    __tablename__ = "interruptions"
    __table_args__ = {"sqlite_autoincrement": True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(
        ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    pause_time: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )

    session: Mapped[WorkSession] = relationship(back_populates="interruptions")
