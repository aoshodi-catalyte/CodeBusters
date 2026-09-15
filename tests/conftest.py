"""
Test database setup for repositories and API tests.
Ensures both main and audit tables are created in the in‑memory SQLite DB.
"""

from datetime import date

import pytest
from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import AuditBase, Base, get_audit_db, get_db
from employee.employee_role_schema import EmployeeRoleSchema
from employee.employee_schema import EmployeeSchema
from main import app
from tests.factories.auth_factories import manager_token as _manager_token

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
    # Create BOTH main and audit tables
    Base.metadata.create_all(bind=engine)
    AuditBase.metadata.create_all(bind=engine)

    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        AuditBase.metadata.drop_all(bind=engine)


def _seed_acting_manager(db):
    """Insert the employee that manager_token() claims to represent."""
    manager_role = EmployeeRoleSchema(role="manager")
    db.add(manager_role)
    db.flush()
    db.add(
        EmployeeSchema(
            id=1,
            active=True,
            first_name="Test",
            last_name="Manager",
            email="manager@example.com",
            role_id=manager_role.id,
            hourly_rate=20.0,
            hire_date=date(2020, 1, 1),
        )
    )
    db.commit()


@pytest.fixture
def client(db):
    _seed_acting_manager(db)

    def override_get_db():
        yield db

    # Audit DB uses the SAME SQLite session
    def override_get_audit_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_audit_db] = override_get_audit_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def acting_user():
    return "test_user@example.com"


@pytest.fixture
def fake_audit_repo():
    class FakeAuditRepo:
        def record_deactivation(self, item_id, item_name, acting_user, entity_type):
            pass
    return FakeAuditRepo()


@pytest.fixture
def clean_client(db):
    """Client without seeding the acting manager."""
    def override_get_db():
        yield db

    def override_get_audit_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_audit_db] = override_get_audit_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
