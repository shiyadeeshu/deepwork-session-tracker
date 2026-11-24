"""Integration tests for the generated SDK, run against a real uvicorn server.

Uses an isolated in-memory database, so it never touches deepwork.db.
Skipped automatically if the SDK is not installed (pip install ./deepwork_sdk).
"""
import socket
import threading
import time

import pytest
import uvicorn
from sqlalchemy.orm import sessionmaker

from app.database import get_db
from app.main import create_app

deepwork_sdk = pytest.importorskip("deepwork_sdk")

from deepwork_sdk import ApiClient, Configuration  # noqa: E402
from deepwork_sdk.api.sessions_api import SessionsApi  # noqa: E402
from deepwork_sdk.exceptions import ApiException  # noqa: E402
from deepwork_sdk.models.pause_request import PauseRequest  # noqa: E402
from deepwork_sdk.models.session_create import SessionCreate  # noqa: E402


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture
def api(engine):
    TestingSession = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app = create_app()
    app.dependency_overrides[get_db] = override_get_db

    port = _free_port()
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning"))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    deadline = time.time() + 10
    while not server.started:
        if time.time() > deadline:
            raise RuntimeError("test server did not start")
        time.sleep(0.05)

    client = ApiClient(Configuration(host=f"http://127.0.0.1:{port}"))
    yield SessionsApi(client)

    server.should_exit = True
    thread.join(timeout=5)


def test_default_host_is_local_api():
    assert Configuration().host == "http://localhost:8000"


def test_full_session_lifecycle_via_sdk(api):
    s = api.create_session(SessionCreate(title="SDK", goal="g", scheduled_duration=50))
    assert s.status.value == "scheduled"
    assert api.start_session(s.id).status.value == "active"
    assert api.pause_session(s.id, PauseRequest(reason="call")).status.value == "paused"
    assert api.resume_session(s.id).status.value == "active"
    done = api.complete_session(s.id)
    assert done.status.value == "completed"
    assert done.end_time is not None
    assert [i.reason for i in done.interruptions] == ["call"]


def test_interrupted_and_abandoned_via_sdk(api):
    s = api.create_session(SessionCreate(title="noisy", scheduled_duration=25))
    api.start_session(s.id)
    for i in range(4):
        s = api.pause_session(s.id, PauseRequest(reason=f"p{i}"))
        if s.status.value == "paused":
            api.resume_session(s.id)
    assert s.status.value == "interrupted"

    a = api.create_session(SessionCreate(title="gave up", scheduled_duration=25))
    api.start_session(a.id)
    api.pause_session(a.id, PauseRequest(reason="bug"))
    assert api.complete_session(a.id).status.value == "abandoned"


def test_sdk_raises_api_exception_with_status(api):
    s = api.create_session(SessionCreate(title="x", scheduled_duration=10))
    with pytest.raises(ApiException) as conflict:
        api.pause_session(s.id, PauseRequest(reason="too early"))
    assert conflict.value.status == 409

    with pytest.raises(ApiException) as missing:
        api.start_session(9999)
    assert missing.value.status == 404


def test_history_via_sdk(api):
    s = api.create_session(SessionCreate(title="h", scheduled_duration=10))
    api.start_session(s.id)
    api.complete_session(s.id)
    h = api.get_session_history()
    assert h.total_sessions == 1
    assert h.completion_ratio == 1.0
    assert h.status_counts["completed"] == 1
    assert h.sessions[0].id == s.id
