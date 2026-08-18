import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from fastapi import FastAPI
from employee.employee_router import router
from employee.employee_role_schema import EmployeeRoleSchema
from employee.employee_schema import Base
from database import get_db


def override_get_db():
    engine = create_engine("sqlite:///:memory:", echo=False)
    TestingSessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()

    role = EmployeeRoleSchema(role="manager")
    db.add(role)
    db.commit()
    db.refresh(role)

    try:
        yield db
    finally:
        db.close()


app = FastAPI()
app.include_router(router)
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_post_new_employee_success():
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
    assert data["role_id"] is not None


def test_post_new_employee_duplicate_email():
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


def test_post_new_employee_invalid_model():
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


def test_post_new_employee_value_error(monkeypatch):
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


def test_post_new_employee_integrity_error(monkeypatch):
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
