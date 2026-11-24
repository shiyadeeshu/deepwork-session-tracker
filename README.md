# Deep Work Session Tracker

Plan, start, pause, resume and complete focused work sessions; track interruptions and review productivity stats.

**Stack:** FastAPI · SQLite · SQLAlchemy 2 · Alembic · React (Vite) + Axios · Python SDK generated with OpenAPI Generator CLI.

| Part | Location | Highlights |
|---|---|---|
| Backend | [app/](app/) | REST API, Swagger UI, dependency-injected DB and clock, 4xx/5xx error handling |
| Database | [alembic/](alembic/), [seed_data.sql](seed_data.sql) | SQLite schema via Alembic migration, seed data covering every status |
| Frontend | [frontend/](frontend/) | Schedule / start / pause (with reason) / resume / complete, history with stats & charts, live countdown, auto-refresh |
| SDK | [deepwork_sdk/](deepwork_sdk/) | Generated from `/openapi.json`; demo in [sdk_example.py](sdk_example.py) |
| Tests | [tests/](tests/) | 59 pytest tests: endpoints, every business rule, DB constraints, migrations, seed data, SDK |
| Scripts | `setupdev.bat`, `runapplication.bat`, `generate_sdk.bat` | One-command setup, run and SDK regeneration |

---

## 1. Prerequisites (Windows)

| Tool | Needed for | Install |
|---|---|---|
| Python 3.11+ | backend | https://www.python.org/downloads/ (tick "Add to PATH") |
| Node.js LTS | frontend, OpenAPI Generator CLI | `winget install OpenJS.NodeJS.LTS` |
| Java 11+ | OpenAPI Generator CLI (only to regenerate the SDK) | `winget install EclipseAdoptium.Temurin.21.JDK` |

No Docker is used.

## 2. Setup

```bat
setupdev.bat
```

This creates the `env` virtual environment, installs `requirements.txt`, runs `alembic upgrade head` (creates `deepwork.db`), installs the generated SDK into the venv, and runs `npm install` in `frontend/`.

Optional: load sample data (one session for each status):

```bat
env\Scripts\python seed.py
```

## 3. Run

```bat
runapplication.bat
```

It opens two windows: the backend (`python main.py`) and the frontend (`npm start`). The challenge's template ran `python main.py` in the same window, which blocks, so the frontend never started. This script uses `start` to launch each one in its own window instead.

| What | URL |
|---|---|
| Frontend | http://localhost:3000 |
| API | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |
| OpenAPI spec | http://localhost:8000/openapi.json |

To run the parts by hand:

```bat
env\Scripts\activate
python main.py                 :: backend
cd frontend && npm start       :: frontend (second terminal)
```

## 4. Tests

```bat
env\Scripts\activate
pytest
```

The tests use an in-memory database and an injected fake clock, so time-based rules (overdue, abandoned) are checked instantly and `deepwork.db` is never touched. The SDK tests start a real server on a free port.

## 5. Python SDK

The SDK is generated, not hand-written, with the command from the challenge plus `--package-name`, so the import path is `deepwork_sdk`:

```bat
npm install -g @openapitools/openapi-generator-cli
openapi-generator-cli generate -i http://localhost:8000/openapi.json -g python -o deepwork_sdk --package-name deepwork_sdk
pip install ./deepwork_sdk
```

`generate_sdk.bat` does all of this in one step. It exports the spec straight from the code ([export_openapi.py](export_openapi.py)), so the backend doesn't need to be running.

Two things in the API exist to make the generated SDK clean:
- Each route has an explicit `operation_id`, so methods are named `create_session`, `pause_session` and so on, instead of FastAPI's default `create_session_sessions_post`.
- The spec declares `servers: [http://localhost:8000]`, so `ApiClient()` with no arguments points at the local API.

Usage, as in the challenge:

```python
from deepwork_sdk.api.sessions_api import SessionsApi
from deepwork_sdk import ApiClient
from deepwork_sdk.models.session_create import SessionCreate
from deepwork_sdk.models.pause_request import PauseRequest

client = ApiClient()
api = SessionsApi(client)

s = api.create_session(SessionCreate(title="Write report", goal="Intro", scheduled_duration=50))
api.start_session(s.id)
api.pause_session(s.id, PauseRequest(reason="Phone call"))
api.resume_session(s.id)
result = api.complete_session(s.id)
print(result.status)                      # SessionStatus.COMPLETED
print(api.get_session_history().completion_ratio)
```

| SDK method | Endpoint |
|---|---|
| `create_session(SessionCreate)` | `POST /sessions/` |
| `list_sessions()` | `GET /sessions/` |
| `get_session_history()` | `GET /sessions/history` |
| `get_session(id)` | `GET /sessions/{id}` |
| `start_session(id)` | `PATCH /sessions/{id}/start` |
| `pause_session(id, PauseRequest)` | `PATCH /sessions/{id}/pause` |
| `resume_session(id)` | `PATCH /sessions/{id}/resume` |
| `complete_session(id)` | `PATCH /sessions/{id}/complete` |

Errors are raised as `deepwork_sdk.exceptions.ApiException` (`.status`, `.body`). Full demo, with the backend running:

```bat
python sdk_example.py
```

## 6. API

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
| GET | `/health` | Health check |

Errors return `{"detail": "..."}`:

| Code | When |
|---|---|
| 404 | Session doesn't exist |
| 409 | Action not allowed in the current status (e.g. pausing a scheduled session) |
| 422 | Invalid input: empty title, duration ≤ 0 or > 1440, missing pause reason, non-integer id |
| 500 | Unexpected error (logged; generic message returned) |

## 7. Business rules & design decisions

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

The challenge's examples are covered by tests in [tests/test_sessions_api.py](tests/test_sessions_api.py):

| Example | Test |
|---|---|
| 50-min session paused 2× → completed | `test_example_50_min_paused_twice_is_completed` |
| Paused 4× → interrupted | `test_fourth_pause_marks_interrupted` |
| Not resumed after pause → abandoned | `test_complete_while_paused_is_abandoned`, `test_paused_past_allowed_window_becomes_abandoned` |
| Completed 60 min after 50 → overdue | `test_example_completed_60_min_after_50_is_overdue` |

## 8. Frontend

React + Vite on http://localhost:3000. It talks to the API only through Axios ([frontend/src/api/client.js](frontend/src/api/client.js)). Set `VITE_API_URL` to point it at a different backend. Create React App is deprecated, so the app uses Vite, with an `npm start` script so the standard commands still work.

- **Sessions tab:** schedule a session (title, goal, minutes, with 25/50/90 presets). Each card shows only the actions valid for its status: Start / Pause (asks for a reason) / Resume / Complete. Completing a paused session asks for confirmation because it marks the session abandoned.
- **Live countdown (bonus)** for active and paused sessions. It shows when you're over time, how long is left before the 10% grace runs out, and warns when the next pause would interrupt the session.
- **History tab** (`#history`): completion ratio, focus time, average duration, pauses, **charts (bonus)** of outcomes and planned-vs-actual minutes, and a table of past sessions with interruption reasons.
- **Real-time updates (bonus):** both views poll the API (every 5 s / 10 s, paused while the tab is hidden), so statuses the server changes on its own, like abandoned, appear without a reload.
- API errors (404/409/422, backend unreachable) are shown inline next to the action that caused them.

## 9. Project structure

```
app/
  main.py              FastAPI app factory, CORS, error handlers
  config.py            settings (env-overridable) + rule constants
  database.py          engine, SQLite FK pragma, get_db dependency
  clock.py             injectable "now" (lets tests control time)
  models.py            SQLAlchemy models
  schemas.py           Pydantic request/response models (= OpenAPI schemas)
  services.py          state machine & business rules
  exceptions.py        domain errors -> HTTP status codes
  routers/sessions.py  HTTP layer
alembic/               migrations (0001 creates both tables)
tests/                 pytest suite
frontend/src/
  api/client.js        Axios instance, all API calls, error formatting
  hooks/               usePolling (live refresh), useNow (1 s ticker)
  components/          SessionForm, SessionCard, Countdown, SessionsView, HistoryView, StatusBadge
deepwork_sdk/          generated Python SDK (do not edit by hand)
main.py                `python main.py` -> uvicorn on :8000
seed_data.sql, seed.py sample data + loader (no sqlite3 CLI needed)
export_openapi.py      writes openapi.json from the code
openapi.json           exported spec used to generate the SDK
sdk_example.py         SDK demo
setupdev.bat / runapplication.bat / generate_sdk.bat
```

## 10. Configuration

| Env var | Default | Purpose |
|---|---|---|
| `DEEPWORK_DATABASE_URL` | `sqlite:///./deepwork.db` | Database used by the API and Alembic |
| `DEEPWORK_CORS_ORIGINS` | `http://localhost:3000,http://localhost:5173` | Browser origins allowed to call the API |
| `DEEPWORK_API_URL` | `http://localhost:8000` | Server URL in the OpenAPI spec (SDK default host) |
| `VITE_API_URL` | `http://localhost:8000` | API base URL used by the frontend |

## 11. Troubleshooting

- **`node` / `java` not recognized right after installing:** restart the terminal, or VS Code, so it picks up the new PATH.
- **Port 8000 or 3000 in use:** close the old backend or frontend window, or stop the process using the port.
- **Frontend says "Cannot reach the API":** the backend isn't running. Start it with `python main.py`.
- **Reset the database:** delete `deepwork.db`, then run `alembic upgrade head` (and `python seed.py` for sample data).
