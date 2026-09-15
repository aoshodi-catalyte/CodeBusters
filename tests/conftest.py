"""
Test database setup for repositories and API tests.
Ensures both main and audit tables are created in the in‑memory SQLite DB.
"""

from datetime import date

from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base, AuditBase, get_audit_db, get_db
from employee.employee_role_schema import EmployeeRoleSchema
from employee.employee_schema import EmployeeSchema
from main import app
from constants.employee_roles import EmployeeRole
from employee.employee_role_schema import EmployeeRoleSchema


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

    # Seed employee roles only if they do not already exist.
    for role in EmployeeRole:
        existing_role = (
            session.query(EmployeeRoleSchema)
            .filter(EmployeeRoleSchema.role == role.value)
            .first()
        )

        if existing_role is None:
            session.add(
                EmployeeRoleSchema(
                    role=role.value,
                )
            )

    session.commit()

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