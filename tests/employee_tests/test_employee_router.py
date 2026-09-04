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

TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)


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
    assert response.json()[
        "detail"] == "Employee with this email already exists."


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
    assert response.json()[
        "detail"] == "Employee with this email already exists."


def test_get_all_employees_empty(client):
    """Test retrieving employees when none exist."""
    response = client.get("/employees")

    assert response.status_code == 200
    assert response.json() == []


def test_get_all_employees(client):
    """Test retrieving all employees."""
    payload_1 = {
        "active": True,
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@doe.com",
        "role": "manager",
        "hourly_rate": "10.50",
        "hire_date": "01/01/2023",
        "term_date": None,
    }

    payload_2 = {
        "active": True,
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "jane@doe.com",
        "role": "manager",
        "hourly_rate": "15.00",
        "hire_date": "02/01/2023",
        "term_date": None,
    }

    client.post("/employees", json=payload_1)
    client.post("/employees", json=payload_2)

    response = client.get("/employees")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["first_name"] == "John"
    assert data[0]["email"] == "john@doe.com"
    assert data[0]["role"] == "manager"
    assert data[1]["first_name"] == "Jane"
    assert data[1]["email"] == "jane@doe.com"


def test_get_all_employees_response_contains_expected_fields(client):
    """Test that employee list response contains expected fields."""
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

    response = client.get("/employees")

    assert response.status_code == 200

    employee = response.json()[0]

    assert "id" in employee
    assert "active" in employee
    assert "first_name" in employee
    assert "last_name" in employee
    assert "email" in employee
    assert "role" in employee


def test_get_single_employee_by_id_success(client):
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

    post_response = client.post("/employees", json=payload)
    assert post_response.status_code == 201

    created = post_response.json()
    employee_id = created["id"]

    get_response = client.get(f"/employees/{employee_id}")

    assert get_response.status_code == 200
    data = get_response.json()

    assert data["id"] == employee_id
    assert data["first_name"] == "John"
    assert data["last_name"] == "Doe"
    assert data["email"] == "john@doe.com"
    assert data["role"] == "manager"
    assert data["active"] is True


def test_get_single_employee_by_id_not_found(client):
    response = client.get("/employees/999")

    assert response.status_code == 404
    assert "Employee with ID" in response.json()["detail"]


def test_get_single_employee_by_id_invalid_id_type(client):
    response = client.get("/employees/not-an-int")

    assert response.status_code == 422
