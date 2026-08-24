import pytest

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import get_db
from health.health_router import router as health_router


TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


app = FastAPI()
app.include_router(health_router)


@pytest.fixture
def client():
    """
    Create a test client with a working test database connection.
    """

    def override_get_db():
        db = TestingSessionLocal()

        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)

    app.dependency_overrides.clear()


def test_health_returns_200(client):
    """
    Verify that the health endpoint returns HTTP 200 when the
    application is running.
    """

    response = client.get("/health")

    assert response.status_code == 200

    assert response.json() == {
        "status": "ok"
    }


def test_ready_returns_200_when_database_is_available(client):
    """
    Verify that the readiness endpoint returns HTTP 200 when the
    database is reachable.
    """

    response = client.get("/ready")

    assert response.status_code == 200

    assert response.json() == {
        "status": "ready"
    }


def test_ready_returns_503_when_database_is_unavailable():
    """
    Verify that the readiness endpoint returns HTTP 503 when the
    database cannot be reached.
    """

    class UnavailableDatabase:
        """
        Simulates a database connection that fails when queried.
        """

        def execute(self, *args, **kwargs):
            raise Exception("Database is unavailable")

    def override_get_db():
        yield UnavailableDatabase()

    app.dependency_overrides[get_db] = override_get_db

    client = TestClient(app)

    response = client.get("/ready")

    assert response.status_code == 503

    assert response.json() == {
        "detail": "Database is unavailable."
    }

    app.dependency_overrides.clear()


def test_health_returns_200_when_database_is_unavailable():
    """
    Verify that the health endpoint returns HTTP 200 even when the
    database is unavailable.
    """

    def override_get_db():
        raise Exception("Database is unavailable")

        yield

    app.dependency_overrides[get_db] = override_get_db

    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200

    assert response.json() == {
        "status": "ok"
    }

    app.dependency_overrides.clear()