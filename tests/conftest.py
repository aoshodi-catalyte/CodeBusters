from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base, get_audit_db, get_db
from main import app

TEST_DB_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db):
    def override_get_db():
        yield db

    # NEW: override audit DB so DELETE works
    def override_get_audit_db():
        class FakeAuditSession:
            def add(self, *args, **kwargs): pass
            def commit(self): pass
            def refresh(self, *args, **kwargs): pass
            def close(self): pass

        yield FakeAuditSession()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_audit_db] = override_get_audit_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
