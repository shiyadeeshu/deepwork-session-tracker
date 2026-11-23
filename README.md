# Deep Work Session Tracker

Plan, start, pause, resume and complete focused work sessions; track interruptions and review productivity stats.

**Stack:** FastAPI · SQLite · SQLAlchemy 2 · Alembic · React + Axios · Python SDK generated with OpenAPI Generator.

## Prerequisites (Windows)

| Tool | Needed for |
|---|---|
| Python 3.11+ | backend |
| Node.js LTS (npm) | frontend, OpenAPI Generator CLI |
| Java 11+ | OpenAPI Generator CLI (SDK generation only) |

## Quick start

```bat
setupdev.bat          :: venv, pip install, alembic upgrade head, npm install
env\Scripts\python seed.py   :: optional: load seed_data.sql
runapplication.bat    :: opens backend + frontend in separate windows
```

- API: http://localhost:8000 · Swagger UI: http://localhost:8000/docs · OpenAPI: http://localhost:8000/openapi.json

## Frontend (React + Vite + Axios)

Runs at http://localhost:3000 and talks to the API only through Axios ([frontend/src/api/client.js](frontend/src/api/client.js)). Set `VITE_API_URL` to point it at a different backend.

```bat
cd frontend
npm start        :: dev server on :3000
npm run build    :: production build into frontend/dist
```

Features:
- **Sessions tab:** schedule a session (title, goal, minutes, with 25/50/90 presets). Each card shows only the actions valid for its status: Start / Pause (asks for a reason) / Resume / Complete. Completing a paused session asks for confirmation because it marks the session abandoned.
- **Live countdown** for active and paused sessions. It shows when you're over time, how long is left before the 10% grace runs out, and warns when the next pause would interrupt the session.
- **History tab** (`#history`): completion ratio, focus time, average duration, pauses, an outcomes chart, a planned-vs-actual chart, and a table of past sessions with interruption reasons.
- **Real-time updates:** both views poll the API (every 5 s / 10 s, paused while the tab is hidden), so statuses the server changes on its own, like abandoned, appear without a reload.
- API errors (404/409/422, backend unreachable) are shown inline next to the action that caused them.

## Running tests

```bat
env\Scripts\activate
pytest
```

## API

| Method | Path | Description |
|---|---|---|
| POST | `/sessions/` | Schedule a session (`title`, `goal`, `scheduled_duration` in minutes) |
| GET | `/sessions/` | List all sessions |
| GET | `/sessions/history` | Summary of past sessions: durations, pauses, completion ratio |
| GET | `/sessions/{id}` | Get one session |
| PATCH | `/sessions/{id}/start` | Start a scheduled session |
| PATCH | `/sessions/{id}/pause` | Pause an active session; body `{"reason": "..."}` |
| PATCH | `/sessions/{id}/resume` | Resume a paused session |
| PATCH | `/sessions/{id}/complete` | Complete the session (stores completion time) |

Errors return `{"detail": "..."}`: **404** unknown session, **409** action not allowed in the current status, **422** invalid input, **500** unexpected error.

## Business rules & design decisions

```
scheduled --start--> active --pause--> paused --resume--> active
active  --complete--> completed | overdue
paused  --complete--> abandoned
active  --4th pause--> interrupted
paused  --allowed window expires--> abandoned
```

1. **Pause only when active.** Otherwise 409.
2. **More than 3 pauses → `interrupted`.** The 4th pause is logged and immediately ends the session (`end_time` = that pause). The session is final.
3. **Overdue.** Completing later than `scheduled_duration × 1.1` after `start_time` → `overdue`, otherwise `completed`. Elapsed time is **wall-clock, pauses included**. The schema stores no resume times, and the spec example ("completed 60 min after 50") reads as wall-clock. Exactly at the limit (55 of 50 min) is still `completed`.
4. **Never resumed after a pause → `abandoned`.** There's no background worker, so this is detected:
   - when `/complete` is called on a **paused** session, and
   - lazily, whenever sessions are read, if a session is still paused after its allowed window (start + duration × 1.1) has passed. Such a session can no longer be resumed (409).

   For abandoned sessions `end_time` = the last pause time, when work actually stopped.
5. **Final states** (`completed`, `overdue`, `interrupted`, `abandoned`) accept no further actions.
6. **Completion ratio** = `completed / finished sessions`. Overdue counts as finished but not as completed.
7. All timestamps are stored as UTC and returned with a `Z` suffix.

## Project structure

```
app/
  main.py            FastAPI app factory, CORS, error handlers
  config.py          settings (env-overridable) + rule constants
  database.py        engine, SQLite FK pragma, get_db dependency
  clock.py           injectable "now" (lets tests control time)
  models.py          SQLAlchemy models
  schemas.py         Pydantic request/response models
  services.py        state machine & business rules
  exceptions.py      domain errors -> HTTP status codes
  routers/sessions.py
alembic/             migrations
tests/               pytest suite (API, rules, DB, migrations, seed)
seed_data.sql, seed.py
main.py              `python main.py` -> uvicorn on :8000
frontend/src/
  api/client.js      Axios instance + all API calls + error formatting
  hooks/             usePolling (live refresh), useNow (1 s ticker)
  components/        SessionForm, SessionCard, Countdown, SessionsView, HistoryView, StatusBadge
```
