"""API tests: CRUD-ish flow, validation, error codes and the 'trick' business rules."""
import pytest


def act(client, sid: int, action: str, reason: str | None = None):
    body = {"reason": reason} if reason is not None else None
    return client.patch(f"/sessions/{sid}/{action}", json=body)


def started(client, make_session, duration=50) -> int:
    sid = make_session(duration)["id"]
    assert act(client, sid, "start").status_code == 200
    return sid


# ---------------------------------------------------------------- create

def test_create_session_returns_201_and_scheduled(make_session):
    s = make_session(50, title="Write report", goal="Intro")
    assert s["status"] == "scheduled"
    assert s["title"] == "Write report"
    assert s["goal"] == "Intro"
    assert s["scheduled_duration"] == 50
    assert s["start_time"] is None and s["end_time"] is None
    assert s["pause_count"] == 0 and s["interruptions"] == []


def test_create_session_goal_optional(client):
    r = client.post("/sessions/", json={"title": "No goal", "scheduled_duration": 25})
    assert r.status_code == 201
    assert r.json()["goal"] is None


@pytest.mark.parametrize(
    "payload",
    [
        {"title": "", "scheduled_duration": 50},          # empty title
        {"title": "   ", "scheduled_duration": 50},       # whitespace-only title
        {"title": "x", "scheduled_duration": 0},          # non-positive duration
        {"title": "x", "scheduled_duration": -5},
        {"title": "x", "scheduled_duration": 2000},       # > 24h
        {"title": "x", "scheduled_duration": "fifty"},    # wrong type
        {"scheduled_duration": 50},                       # missing title
        {"title": "x"},                                   # missing duration
    ],
)
def test_create_session_validation_errors(client, payload):
    assert client.post("/sessions/", json=payload).status_code == 422


# ---------------------------------------------------------------- 404s

@pytest.mark.parametrize("action", ["start", "resume", "complete"])
def test_unknown_session_returns_404(client, action):
    r = act(client, 999, action)
    assert r.status_code == 404
    assert r.json() == {"detail": "Session 999 not found"}


def test_pause_unknown_session_returns_404(client):
    assert act(client, 999, "pause", "x").status_code == 404


def test_get_unknown_session_returns_404(client):
    assert client.get("/sessions/999").status_code == 404


def test_non_integer_id_returns_422(client):
    assert client.patch("/sessions/abc/start").status_code == 422


# ---------------------------------------------------------------- start

def test_start_sets_active_and_start_time(client, make_session, clock):
    sid = make_session()["id"]
    r = act(client, sid, "start")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "active"
    assert body["start_time"].startswith("2026-01-01T09:00:00")
    assert body["start_time"].endswith(("Z", "+00:00"))  # timezone-aware UTC


def test_cannot_start_twice(client, make_session):
    sid = started(client, make_session)
    r = act(client, sid, "start")
    assert r.status_code == 409
    assert "active" in r.json()["detail"]


# ---------------------------------------------------------------- pause / resume

def test_pause_logs_interruption_reason(client, make_session, clock):
    sid = started(client, make_session)
    clock.advance(10)
    r = act(client, sid, "pause", "Phone call")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "paused"
    assert body["pause_count"] == 1
    assert body["interruptions"][0]["reason"] == "Phone call"
    assert body["interruptions"][0]["pause_time"].startswith("2026-01-01T09:10:00")


def test_cannot_pause_scheduled_session(client, make_session):
    sid = make_session()["id"]
    assert act(client, sid, "pause", "x").status_code == 409


def test_cannot_pause_already_paused_session(client, make_session):
    sid = started(client, make_session)
    act(client, sid, "pause", "first")
    r = act(client, sid, "pause", "second")
    assert r.status_code == 409
    # the rejected pause must not be logged
    assert client.get(f"/sessions/{sid}").json()["pause_count"] == 1


def test_cannot_pause_finished_session(client, make_session):
    sid = started(client, make_session)
    act(client, sid, "complete")
    assert act(client, sid, "pause", "x").status_code == 409


@pytest.mark.parametrize("body", [None, {}, {"reason": ""}, {"reason": "   "}])
def test_pause_requires_reason(client, make_session, body):
    sid = started(client, make_session)
    assert client.patch(f"/sessions/{sid}/pause", json=body).status_code == 422


def test_resume_returns_to_active(client, make_session):
    sid = started(client, make_session)
    act(client, sid, "pause", "x")
    r = act(client, sid, "resume")
    assert r.status_code == 200
    assert r.json()["status"] == "active"


@pytest.mark.parametrize("setup", ["scheduled", "active"])
def test_cannot_resume_unless_paused(client, make_session, setup):
    sid = make_session()["id"] if setup == "scheduled" else started(client, make_session)
    assert act(client, sid, "resume").status_code == 409


# ---------------------------------------------------------------- rule: interrupted

def test_three_pauses_is_still_fine(client, make_session):
    sid = started(client, make_session)
    for i in range(3):
        assert act(client, sid, "pause", f"p{i}").json()["status"] == "paused"
        act(client, sid, "resume")
    assert act(client, sid, "complete").json()["status"] == "completed"


def test_fourth_pause_marks_interrupted(client, make_session, clock):
    """Example: paused 4x -> interrupted."""
    sid = started(client, make_session)
    for i in range(3):
        act(client, sid, "pause", f"p{i}")
        act(client, sid, "resume")
    clock.advance(20)
    r = act(client, sid, "pause", "p4")
    body = r.json()
    assert r.status_code == 200
    assert body["status"] == "interrupted"
    assert body["pause_count"] == 4
    assert body["end_time"].startswith("2026-01-01T09:20:00")


def test_interrupted_session_is_final(client, make_session):
    sid = started(client, make_session)
    for i in range(3):
        act(client, sid, "pause", f"p{i}")
        act(client, sid, "resume")
    act(client, sid, "pause", "p4")
    for action in ("resume", "complete", "start"):
        assert act(client, sid, action).status_code == 409


# ---------------------------------------------------------------- rule: completed / overdue

def test_example_50_min_paused_twice_is_completed(client, make_session, clock):
    """Example: 50-min session paused 2x -> completed."""
    sid = started(client, make_session, 50)
    clock.advance(10); act(client, sid, "pause", "a")
    clock.advance(2);  act(client, sid, "resume")
    clock.advance(10); act(client, sid, "pause", "b")
    clock.advance(2);  act(client, sid, "resume")
    clock.advance(26)  # total 50 minutes
    body = act(client, sid, "complete").json()
    assert body["status"] == "completed"
    assert body["end_time"].startswith("2026-01-01T09:50:00")


def test_example_completed_60_min_after_50_is_overdue(client, make_session, clock):
    """Example: completed 60 mins after a 50-min schedule -> overdue."""
    sid = started(client, make_session, 50)
    clock.advance(60)
    assert act(client, sid, "complete").json()["status"] == "overdue"


def test_completing_exactly_at_10_percent_limit_is_completed(client, make_session, clock):
    sid = started(client, make_session, 50)
    clock.advance(55)  # 50 + 10%
    assert act(client, sid, "complete").json()["status"] == "completed"


def test_completing_just_past_limit_is_overdue(client, make_session, clock):
    sid = started(client, make_session, 50)
    clock.advance(55.1)
    assert act(client, sid, "complete").json()["status"] == "overdue"


def test_finishing_early_is_completed(client, make_session, clock):
    sid = started(client, make_session, 50)
    clock.advance(20)
    assert act(client, sid, "complete").json()["status"] == "completed"


def test_cannot_complete_scheduled_session(client, make_session):
    sid = make_session()["id"]
    assert act(client, sid, "complete").status_code == 409


def test_cannot_complete_twice(client, make_session):
    sid = started(client, make_session)
    act(client, sid, "complete")
    assert act(client, sid, "complete").status_code == 409


# ---------------------------------------------------------------- rule: abandoned

def test_complete_while_paused_is_abandoned(client, make_session, clock):
    """Example: not resumed after pause -> abandoned."""
    sid = started(client, make_session, 50)
    clock.advance(15)
    act(client, sid, "pause", "Got pulled into a meeting")
    clock.advance(10)
    body = act(client, sid, "complete").json()
    assert body["status"] == "abandoned"
    # end_time is when work actually stopped (the pause), not when complete was called
    assert body["end_time"].startswith("2026-01-01T09:15:00")


def test_paused_past_allowed_window_becomes_abandoned(client, make_session, clock):
    sid = started(client, make_session, 50)
    clock.advance(10)
    act(client, sid, "pause", "Left desk")
    clock.advance(46)  # 56 min since start > 55-min window, still paused
    body = client.get(f"/sessions/{sid}").json()
    assert body["status"] == "abandoned"
    assert body["end_time"].startswith("2026-01-01T09:10:00")


def test_resume_after_window_expired_is_rejected(client, make_session, clock):
    sid = started(client, make_session, 50)
    act(client, sid, "pause", "Left desk")
    clock.advance(60)
    r = act(client, sid, "resume")
    assert r.status_code == 409
    assert "abandoned" in r.json()["detail"]


def test_paused_within_window_is_not_abandoned(client, make_session, clock):
    sid = started(client, make_session, 50)
    act(client, sid, "pause", "short break")
    clock.advance(30)
    assert client.get(f"/sessions/{sid}").json()["status"] == "paused"
    assert act(client, sid, "resume").json()["status"] == "active"


# ---------------------------------------------------------------- list / history

def test_list_sessions_newest_first(client, make_session):
    a = make_session(title="A")["id"]
    b = make_session(title="B")["id"]
    ids = [s["id"] for s in client.get("/sessions/").json()]
    assert ids == [b, a]


def test_history_empty(client):
    body = client.get("/sessions/history").json()
    assert body["total_sessions"] == 0
    assert body["finished_sessions"] == 0
    assert body["completion_ratio"] == 0.0
    assert body["sessions"] == []


def test_history_summary_stats(client, make_session, clock):
    # completed in 40 min with 2 pauses
    s1 = started(client, make_session, 50)
    act(client, s1, "pause", "a"); act(client, s1, "resume")
    act(client, s1, "pause", "b"); act(client, s1, "resume")
    clock.advance(40); act(client, s1, "complete")
    # overdue: 20 min session done in 30
    s2 = started(client, make_session, 20)
    clock.advance(30); act(client, s2, "complete")
    # abandoned
    s3 = started(client, make_session, 30)
    act(client, s3, "pause", "gone"); act(client, s3, "complete")
    # still scheduled (not "past") -> counted in totals, not in finished
    make_session(25)

    h = client.get("/sessions/history").json()
    assert h["total_sessions"] == 4
    assert h["finished_sessions"] == 3
    assert h["status_counts"]["completed"] == 1
    assert h["status_counts"]["overdue"] == 1
    assert h["status_counts"]["abandoned"] == 1
    assert h["status_counts"]["scheduled"] == 1
    assert h["completion_ratio"] == pytest.approx(1 / 3, abs=1e-4)
    assert h["total_pauses"] == 3
    assert h["average_pauses_per_session"] == pytest.approx(0.75)
    assert h["total_focus_minutes"] == pytest.approx(40 + 30 + 0)
    assert h["average_duration_minutes"] == pytest.approx(70 / 3, abs=0.01)
    assert {s["id"] for s in h["sessions"]} == {s1, s2, s3}
    durations = {s["id"]: s["actual_duration_minutes"] for s in h["sessions"]}
    assert durations == {s1: 40.0, s2: 30.0, s3: 0.0}


def test_history_applies_lazy_abandonment(client, make_session, clock):
    sid = started(client, make_session, 10)
    act(client, sid, "pause", "x")
    clock.advance(30)
    h = client.get("/sessions/history").json()
    assert h["status_counts"]["abandoned"] == 1
    assert h["sessions"][0]["id"] == sid


# ---------------------------------------------------------------- OpenAPI

def test_openapi_and_docs_available(client):
    assert client.get("/docs").status_code == 200
    spec = client.get("/openapi.json").json()
    op_ids = {op["operationId"] for path in spec["paths"].values() for op in path.values()}
    assert {
        "create_session", "start_session", "pause_session", "resume_session",
        "complete_session", "get_session_history",
    } <= op_ids
    statuses = spec["components"]["schemas"]["SessionStatus"]["enum"]
    assert set(statuses) == {
        "scheduled", "active", "paused", "completed", "interrupted", "abandoned", "overdue",
    }
