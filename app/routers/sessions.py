"""HTTP layer for /sessions. Thin: validates input, injects deps, delegates to services.

Explicit `operation_id`s give the generated SDK clean method names
(e.g. `SessionsApi.start_session`) instead of FastAPI's auto-generated ones.
"""
from datetime import datetime

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app import services
from app.clock import get_now
from app.database import get_db
from app.schemas import (
    ErrorResponse,
    HistorySummary,
    PauseRequest,
    SessionCreate,
    SessionRead,
)

router = APIRouter(prefix="/sessions", tags=["sessions"])

NOT_FOUND = {404: {"model": ErrorResponse, "description": "Session not found"}}
CONFLICT = {409: {"model": ErrorResponse, "description": "Action not allowed in the current status"}}

Db = Depends(get_db)
Now = Depends(get_now)


@router.post(
    "/",
    response_model=SessionRead,
    status_code=status.HTTP_201_CREATED,
    operation_id="create_session",
    summary="Schedule a new work session",
)
def create_session(payload: SessionCreate, db: Session = Db):
    return services.create_session(db, payload)


@router.get(
    "/",
    response_model=list[SessionRead],
    operation_id="list_sessions",
    summary="List all sessions (newest first)",
)
def list_sessions(db: Session = Db, now: datetime = Now):
    return services.list_sessions(db, now)


# Declared before /{session_id} so 'history' is never parsed as an id.
@router.get(
    "/history",
    response_model=HistorySummary,
    operation_id="get_session_history",
    summary="Summary of past sessions: durations, pauses, completion ratio",
)
def get_history(db: Session = Db, now: datetime = Now):
    return services.get_history(db, now)


@router.get(
    "/{session_id}",
    response_model=SessionRead,
    responses=NOT_FOUND,
    operation_id="get_session",
    summary="Get one session",
)
def get_session(session_id: int, db: Session = Db, now: datetime = Now):
    return services.get_session(db, session_id, now)


@router.patch(
    "/{session_id}/start",
    response_model=SessionRead,
    responses={**NOT_FOUND, **CONFLICT},
    operation_id="start_session",
    summary="Start a scheduled session",
)
def start_session(session_id: int, db: Session = Db, now: datetime = Now):
    return services.start_session(db, session_id, now)


@router.patch(
    "/{session_id}/pause",
    response_model=SessionRead,
    responses={**NOT_FOUND, **CONFLICT},
    operation_id="pause_session",
    summary="Pause an active session and log the interruption reason",
    description="Only active sessions can be paused. The 4th pause marks the session `interrupted`.",
)
def pause_session(session_id: int, payload: PauseRequest, db: Session = Db, now: datetime = Now):
    return services.pause_session(db, session_id, payload.reason, now)


@router.patch(
    "/{session_id}/resume",
    response_model=SessionRead,
    responses={**NOT_FOUND, **CONFLICT},
    operation_id="resume_session",
    summary="Resume a paused session",
)
def resume_session(session_id: int, db: Session = Db, now: datetime = Now):
    return services.resume_session(db, session_id, now)


@router.patch(
    "/{session_id}/complete",
    response_model=SessionRead,
    responses={**NOT_FOUND, **CONFLICT},
    operation_id="complete_session",
    summary="Complete a session (stores completion time)",
    description=(
        "Active → `completed` if finished within scheduled duration + 10%, else `overdue`. "
        "Paused (never resumed) → `abandoned`."
    ),
)
def complete_session(session_id: int, db: Session = Db, now: datetime = Now):
    return services.complete_session(db, session_id, now)
