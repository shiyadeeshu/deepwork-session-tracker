"""Business logic: the session state machine and the 'trick' rules.

State machine
-------------
    scheduled --start--> active --pause--> paused --resume--> active
    active --complete--> completed | overdue
    paused --complete--> abandoned           (it was never resumed)
    active --pause (4th time)--> interrupted (more than MAX_PAUSES pauses)
    paused --(allowed window expires)--> abandoned

Rules
-----
* Pause is only allowed while active.
* Pausing more than MAX_PAUSES (3) times marks the session interrupted.
* Completion later than scheduled_duration * (1 + OVERDUE_TOLERANCE) after start
  (wall-clock, pauses included) marks it overdue; otherwise completed.
* A paused session that is never resumed becomes abandoned. Detected:
    - when /complete is called while still paused, or
    - lazily, whenever a session is read, if its allowed window (the overdue
      deadline) has passed while it is still paused.
  For abandoned sessions end_time = the last pause time (when work actually stopped).
"""
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import config
from app.exceptions import InvalidStateTransitionError, SessionNotFoundError
from app.models import TERMINAL_STATUSES, Interruption, SessionStatus, WorkSession
from app.schemas import HistorySummary, SessionCreate, SessionHistoryItem

S = SessionStatus


# ---------- helpers ----------

def deadline(ws: WorkSession) -> datetime:
    """Latest moment the session may be completed without being overdue."""
    allowed = ws.scheduled_duration * (1 + config.OVERDUE_TOLERANCE)
    return ws.start_time + timedelta(minutes=allowed)


def _require(ws: WorkSession, action: str, *allowed: SessionStatus) -> None:
    if ws.status not in {a.value for a in allowed}:
        raise InvalidStateTransitionError(action, ws.status, [a.value for a in allowed])


def _mark_abandoned_if_expired(ws: WorkSession, now: datetime) -> bool:
    """Lazy rule: still paused after the allowed window -> abandoned. Returns True if changed."""
    if ws.status == S.paused.value and ws.start_time and now > deadline(ws):
        ws.status = S.abandoned.value
        ws.end_time = ws.interruptions[-1].pause_time
        return True
    return False


def _get(db: Session, session_id: int, now: datetime) -> WorkSession:
    ws = db.get(WorkSession, session_id)
    if ws is None:
        raise SessionNotFoundError(session_id)
    if _mark_abandoned_if_expired(ws, now):
        db.commit()
    return ws


def _save(db: Session, ws: WorkSession) -> WorkSession:
    db.commit()
    db.refresh(ws)
    return ws


# ---------- commands ----------

def create_session(db: Session, data: SessionCreate) -> WorkSession:
    ws = WorkSession(**data.model_dump(), status=S.scheduled.value)
    db.add(ws)
    return _save(db, ws)


def start_session(db: Session, session_id: int, now: datetime) -> WorkSession:
    ws = _get(db, session_id, now)
    _require(ws, "start", S.scheduled)
    ws.status = S.active.value
    ws.start_time = now
    return _save(db, ws)


def pause_session(db: Session, session_id: int, reason: str, now: datetime) -> WorkSession:
    ws = _get(db, session_id, now)
    _require(ws, "pause", S.active)
    ws.interruptions.append(Interruption(reason=reason, pause_time=now))
    if ws.pause_count > config.MAX_PAUSES:
        ws.status = S.interrupted.value
        ws.end_time = now
    else:
        ws.status = S.paused.value
    return _save(db, ws)


def resume_session(db: Session, session_id: int, now: datetime) -> WorkSession:
    ws = _get(db, session_id, now)  # may flip to abandoned if the window expired
    _require(ws, "resume", S.paused)
    ws.status = S.active.value
    return _save(db, ws)


def complete_session(db: Session, session_id: int, now: datetime) -> WorkSession:
    ws = _get(db, session_id, now)
    _require(ws, "complete", S.active, S.paused)
    if ws.status == S.paused.value:
        ws.status = S.abandoned.value
        ws.end_time = ws.interruptions[-1].pause_time
    else:
        ws.end_time = now
        ws.status = (S.overdue if now > deadline(ws) else S.completed).value
    return _save(db, ws)


# ---------- queries ----------

def _all_sessions(db: Session, now: datetime) -> list[WorkSession]:
    sessions = list(db.scalars(select(WorkSession).order_by(WorkSession.id.desc())))
    if any([_mark_abandoned_if_expired(ws, now) for ws in sessions]):
        db.commit()
    return sessions


def get_session(db: Session, session_id: int, now: datetime) -> WorkSession:
    return _get(db, session_id, now)


def list_sessions(db: Session, now: datetime) -> list[WorkSession]:
    return _all_sessions(db, now)


def get_history(db: Session, now: datetime) -> HistorySummary:
    sessions = _all_sessions(db, now)
    finished = [ws for ws in sessions if ws.status in {s.value for s in TERMINAL_STATUSES}]

    status_counts = {s: 0 for s in SessionStatus}
    for ws in sessions:
        status_counts[SessionStatus(ws.status)] += 1

    durations = [ws.actual_duration_minutes for ws in finished
                 if ws.actual_duration_minutes is not None]
    total_pauses = sum(ws.pause_count for ws in sessions)

    def ratio(a: float, b: float) -> float:
        return round(a / b, 4) if b else 0.0

    return HistorySummary(
        total_sessions=len(sessions),
        finished_sessions=len(finished),
        status_counts=status_counts,
        completion_ratio=ratio(status_counts[S.completed], len(finished)),
        total_pauses=total_pauses,
        average_pauses_per_session=ratio(total_pauses, len(sessions)),
        total_focus_minutes=round(sum(durations), 2),
        average_duration_minutes=ratio(sum(durations), len(durations)),
        sessions=[SessionHistoryItem.model_validate(ws) for ws in finished],
    )
