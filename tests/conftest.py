from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.clock import get_now
from app.database import Base, get_db, make_engine
from app.main import create_app


class FakeClock:
    """Controllable 'now' so time-based rules can be tested instantly."""

    def __init__(self, start: datetime = datetime(2026, 1, 1, 9, 0, 0)):
        self.now = start

    def advance(self, minutes: float) -> None:
        self.now += timedelta(minutes=minutes)

    def __call__(self) -> datetime:
        return self.now


@pytest.fixture
def engine():
    # One shared in-memory DB per test (StaticPool keeps the single connection alive).
    engine = make_engine("sqlite://", poolclass=StaticPool)
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def db_session(engine):
    TestingSession = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    db = TestingSession()
    yield db
    db.close()


@pytest.fixture
def clock():
    return FakeClock()


@pytest.fixture
def client(engine, clock):
    TestingSession = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app = create_app()
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_now] = clock
    with TestClient(app) as c:
        yield c


@pytest.fixture
def make_session(client):
    def _make(duration: int = 50, title: str = "Deep work", goal: str | None = "Ship it") -> dict:
        r = client.post("/sessions/", json={"title": title, "goal": goal, "scheduled_duration": duration})
        assert r.status_code == 201, r.text
        return r.json()

    return _make
