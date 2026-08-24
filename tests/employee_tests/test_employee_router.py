import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from database import Base, get_db
from employee.employee_role_schema import EmployeeRoleSchema
from employee.employee_schema import EmployeeSchema

TEST_DB_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DB_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()

    role = EmployeeRoleSchema(role="manager")
    session.add(role)
    session.commit()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db):

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    yield client
    app.dependency_overrides.clear()


def test_post_new_employee_success(client):
    payload = {
        "active": True,
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@doe.com",
        "role": "manager",
        "hourly_rate": "10.50",
        "hire_date": "01/01/2023",
        "term_date": None,
    }

    response = client.post("/employees", json=payload)

    assert response.status_code == 201
    data = response.json()

    assert data["first_name"] == "John"
    assert data["email"] == "john@doe.com"


def test_post_new_employee_duplicate_email(client):
    payload = {
        "active": True,
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@doe.com",
        "role": "manager",
        "hourly_rate": "10.50",
        "hire_date": "01/01/2023",
        "term_date": None,
    }

    client.post("/employees", json=payload)

    response = client.post("/employees", json=payload)

    assert response.status_code == 409
    assert response.json()["detail"] == "Employee with this email already exists."


def test_post_new_employee_invalid_model(client):
    payload = {
        "active": True,
        "first_name": "John",
        "last_name": "Doe",
        "email": "not-an-email",
        "role": "manager",
        "hourly_rate": "10.50",
        "hire_date": "01/01/2023",
        "term_date": None,
    }

    response = client.post("/employees", json=payload)

    assert response.status_code == 422


def test_post_new_employee_value_error(monkeypatch, client):
    def fake_create_new_employee(*args, **kwargs):
        raise ValueError("Invalid role mapping")

    from repositories.employee_repository import EmployeeRepository

    monkeypatch.setattr(
        EmployeeRepository, "create_new_employee", fake_create_new_employee
    )

    payload = {
        "active": True,
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@doe.com",
        "role": "manager",
        "hourly_rate": "10.50",
        "hire_date": "01/01/2023",
        "term_date": None,
    }

    response = client.post("/employees", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid role mapping"


def test_post_new_employee_integrity_error(monkeypatch, client):
    from sqlalchemy.exc import IntegrityError

    def fake_create_new_employee(*args, **kwargs):
        raise IntegrityError("duplicate", "params", "orig")

    from repositories.employee_repository import EmployeeRepository

    monkeypatch.setattr(
        EmployeeRepository, "create_new_employee", fake_create_new_employee
    )

    payload = {
        "active": True,
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@doe.com",
        "role": "manager",
        "hourly_rate": "10.50",
        "hire_date": "01/01/2023",
        "term_date": None,
    }

    response = client.post("/employees", json=payload)

    assert response.status_code == 409
    assert response.json()["detail"] == "Employee with this email already exists."