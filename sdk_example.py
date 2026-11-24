"""Demonstrates the generated Python SDK (deepwork_sdk) against a running API.

Prerequisites:
    1. Backend running:        python main.py
    2. SDK installed in venv:  pip install ./deepwork_sdk   (setupdev.bat does this)

Run:
    python sdk_example.py
"""
from deepwork_sdk import ApiClient
from deepwork_sdk.api.sessions_api import SessionsApi
from deepwork_sdk.exceptions import ApiException
from deepwork_sdk.models.pause_request import PauseRequest
from deepwork_sdk.models.session_create import SessionCreate


def show(label: str, session) -> None:
    print(f"  {label:<10} -> #{session.id} '{session.title}' status={session.status.value} "
          f"pauses={session.pause_count}")


def main() -> None:
    client = ApiClient()  # default host http://localhost:8000 comes from the OpenAPI spec
    api = SessionsApi(client)

    print("1) Normal flow: schedule, start, pause twice, resume, complete")
    s = api.create_session(SessionCreate(title="SDK demo session", goal="Try the SDK",
                                         scheduled_duration=50))
    show("created", s)
    show("started", api.start_session(s.id))
    for reason in ("Phone call", "Coffee"):
        show("paused", api.pause_session(s.id, PauseRequest(reason=reason)))
        show("resumed", api.resume_session(s.id))
    show("completed", api.complete_session(s.id))

    print("\n2) Rule: more than 3 pauses -> interrupted")
    s = api.create_session(SessionCreate(title="Noisy office", scheduled_duration=25))
    api.start_session(s.id)
    for i in range(1, 5):
        s = api.pause_session(s.id, PauseRequest(reason=f"Interruption {i}"))
        if s.status.value == "paused":
            api.resume_session(s.id)
    show("4th pause", s)

    print("\n3) Rule: paused and never resumed -> abandoned")
    s = api.create_session(SessionCreate(title="Gave up", scheduled_duration=30))
    api.start_session(s.id)
    api.pause_session(s.id, PauseRequest(reason="Urgent bug"))
    show("completed", api.complete_session(s.id))

    print("\n4) Error handling: pausing a session that isn't active")
    s = api.create_session(SessionCreate(title="Not started", scheduled_duration=10))
    try:
        api.pause_session(s.id, PauseRequest(reason="too early"))
    except ApiException as e:
        print(f"  HTTP {e.status}: {e.body}")

    print("\n5) History summary")
    h = api.get_session_history()
    print(f"  total={h.total_sessions} finished={h.finished_sessions} "
          f"completion_ratio={h.completion_ratio:.0%} pauses={h.total_pauses}")
    print(f"  status counts: { {k: v for k, v in h.status_counts.items() if v} }")
    for item in h.sessions[:5]:
        print(f"  - #{item.id} {item.title}: {item.status.value}, "
              f"{item.actual_duration_minutes} of {item.scheduled_duration} min")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # urllib3 connection errors etc.
        if "Connection" in type(exc).__name__ or "Max retries" in str(exc):
            raise SystemExit("Cannot reach http://localhost:8000. Start the backend: python main.py")
        raise
