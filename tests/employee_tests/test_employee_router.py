from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from jose import jwt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from database import Base, get_db
from constants.employee_roles import EmployeeRole
from employee.employee_model import Employee
from employee.employee_role_schema import EmployeeRoleSchema
from employee.employee_schema import EmployeeSchema
from secure_login.secure_login_schema import EmployeeAuth
from services.employee_service import EmployeeService
from services import employee_service


TEST_JWT_SECRET = "test-secret"
TEST_JWT_ALGORITHM = "HS256"


def manager_headers():
    """Create deterministic authorization headers for manager tests."""
    now = datetime.now(UTC)

    payload = {
        "sub": "1",
        "employee_id": 1,
        "role": "manager",
        "jti": str(uuid4()),
        "iat": now,
        "exp": now + timedelta(hours=1),
    }

    token = jwt.encode(
        payload,
        TEST_JWT_SECRET,
        algorithm=TEST_JWT_ALGORITHM,
    )

    return {
        "Authorization": f"Bearer {token}",
    }


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

    response = client.post(
        "/employees",
        json=payload,
        headers=manager_headers(),
    )

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

    client.post(
        "/employees",
        json=payload,
        headers=manager_headers(),
    )

    response = client.post(
        "/employees",
        json=payload,
        headers=manager_headers(),
    )

    assert response.status_code == 409

    assert response.json()[
        "detail"
    ] == "Employee with this email already exists."


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

    response = client.post(
        "/employees",
        json=payload,
        headers=manager_headers(),
    )

    assert response.status_code == 422


def test_post_new_employee_value_error(
    monkeypatch,
    client,
):
    def fake_create_employee(*args, **kwargs):
        raise ValueError("Invalid role mapping")

    monkeypatch.setattr(
        EmployeeService,
        "create_employee",
        fake_create_employee,
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

    response = client.post(
        "/employees",
        json=payload,
        headers=manager_headers(),
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid role mapping"


def test_post_new_employee_integrity_error(
    monkeypatch,
    client,
):
    from sqlalchemy.exc import IntegrityError

    def fake_create_employee(*args, **kwargs):
        raise IntegrityError(
            "duplicate",
            "params",
            "orig",
        )

    monkeypatch.setattr(
        EmployeeService,
        "create_employee",
        fake_create_employee,
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

    response = client.post(
        "/employees",
        json=payload,
        headers=manager_headers(),
    )

    assert response.status_code == 409

    assert response.json()[
        "detail"
    ] == "Employee with this email already exists."


def test_post_new_employee_sends_credentials_and_allows_initial_login(
    client,
    db,
    monkeypatch,
):
    captured = {}

    class FakeEmailService:
        def __init__(self, *args, **kwargs):
            pass

        def send_initial_credentials(
            self,
            recipient_email,
            username,
            temporary_password,
        ):
            captured["recipient_email"] = recipient_email
            captured["username"] = username
            captured["temporary_password"] = temporary_password

    monkeypatch.setattr(
        employee_service,
        "EmailService",
        FakeEmailService,
    )

    payload = {
        "active": True,
        "first_name": "Yemi",
        "last_name": "Onboard",
        "email": "yemi.onboard@example.com",
        "role": "manager",
        "hourly_rate": "20.00",
        "hire_date": "09/16/2026",
        "term_date": None,
    }

    response = client.post(
        "/employees",
        json=payload,
        headers=manager_headers(),
    )

    assert response.status_code == 201

    assert captured["recipient_email"] == (
        "yemi.onboard@example.com"
    )

    assert captured["username"] == "yemi.onboard"

    assert captured["temporary_password"] is not None
    assert captured["temporary_password"] != ""

    auth_record = (
        db.query(EmployeeAuth)
        .filter(
            EmployeeAuth.username
            == captured["username"]
        )
        .first()
    )

    assert auth_record is not None
    assert auth_record.is_temporary_password is True

    login_response = client.post(
        "/auth/login",
        data={
            "username": captured["username"],
            "password": captured["temporary_password"],
        },
    )

    assert login_response.status_code == 200

    login_data = login_response.json()

    assert "access_token" in login_data
    assert login_data["token_type"] == "bearer"
    assert login_data["must_change_password"] is True


def test_get_all_employees_empty(clean_client):
    response = clean_client.get("/employees")

    assert response.status_code == 200
    assert response.json() == []


def test_get_all_employees(client):
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

    client.post(
        "/employees",
        json=payload_1,
        headers=manager_headers(),
    )

    client.post(
        "/employees",
        json=payload_2,
        headers=manager_headers(),
    )

    response = client.get("/employees")

    assert response.status_code == 200

    data = response.json()

    employees = [
        employee
        for employee in data
        if employee["email"] != "manager@example.com"
    ]

    assert len(employees) == 2

    assert employees[0]["first_name"] == "John"
    assert employees[0]["email"] == "john@doe.com"
    assert employees[0]["role"] == "manager"

    assert employees[1]["first_name"] == "Jane"
    assert employees[1]["email"] == "jane@doe.com"


def test_get_all_employees_response_contains_expected_fields(
    client,
):
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

    client.post(
        "/employees",
        json=payload,
        headers=manager_headers(),
    )

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

    post_response = client.post(
        "/employees",
        json=payload,
        headers=manager_headers(),
    )

    assert post_response.status_code == 201

    created = post_response.json()
    employee_id = created["id"]

    get_response = client.get(
        f"/employees/{employee_id}"
    )

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
    response = client.get(
        "/employees/not-an-int"
    )

    assert response.status_code == 422


def test_update_employee_success(client):
    payload = {
        "active": True,
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@doe.com",
        "role": "manager",
        "hourly_rate": 10.50,
        "hire_date": "01/01/2023",
        "term_date": None,
    }

    create_resp = client.post(
        "/employees",
        json=payload,
        headers=manager_headers(),
    )

    employee_id = create_resp.json()["id"]

    update_payload = {
        "active": False,
        "first_name": "Johnny",
        "last_name": "Doe",
        "email": "johnny@doe.com",
        "role": "manager",
        "hourly_rate": 15.00,
        "hire_date": "01/01/2023",
        "term_date": "01/02/2023",
    }

    resp = client.put(
        f"/employees/{employee_id}",
        json=update_payload,
        headers=manager_headers(),
    )

    assert resp.status_code == 200

    data = resp.json()

    assert data["first_name"] == "Johnny"
    assert data["email"] == "johnny@doe.com"
    assert data["active"] is False


def test_update_employee_not_found(client):
    update_payload = {
        "active": True,
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "jane@doe.com",
        "role": "manager",
        "hourly_rate": 12.00,
        "hire_date": "01/01/2023",
        "term_date": None,
    }

    resp = client.put(
        "/employees/999",
        json=update_payload,
        headers=manager_headers(),
    )

    assert resp.status_code == 404
    assert "does not exist" in (
        resp.json()["detail"].lower()
    )


def test_update_employee_invalid_payload(client):
    invalid_payload = {
        "active": True,
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "not-an-email",
        "role": "manager",
        "hourly_rate": 12.00,
        "hire_date": "01/01/2023",
        "term_date": None,
    }

    resp = client.put(
        "/employees/1",
        json=invalid_payload,
        headers=manager_headers(),
    )

    assert resp.status_code == 422


def test_deactivate_employee_success(client):
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

    post_response = client.post(
        "/employees",
        json=payload,
        headers=manager_headers(),
    )

    assert post_response.status_code == 201

    created = post_response.json()
    employee_id = created["id"]

    delete_response = client.delete(
        f"/employees/{employee_id}",
        headers=manager_headers(),
    )

    assert delete_response.status_code == 204


def test_deactivate_employee_not_found(client):
    response = client.delete(
        "/employees/999",
        headers=manager_headers(),
    )

    assert response.status_code == 404
    assert "does not exist" in (
        response.json()["detail"].lower()
    )


def test_deactivate_employee_already_deactivated(client):
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

    post_response = client.post(
        "/employees",
        json=payload,
        headers=manager_headers(),
    )

    assert post_response.status_code == 201

    created = post_response.json()
    employee_id = created["id"]

    first_delete_response = client.delete(
        f"/employees/{employee_id}",
        headers=manager_headers(),
    )

    assert first_delete_response.status_code == 204

    second_delete_response = client.delete(
        f"/employees/{employee_id}",
        headers=manager_headers(),
    )

    assert second_delete_response.status_code == 409

    assert "already deactivated" in (
        second_delete_response.json()["detail"].lower()
    )


def test_employee_can_change_temporary_password_and_login_permanently(
    client,
    db,
    monkeypatch,
):
    captured = {}

    class FakeEmailService:
        def __init__(self, *args, **kwargs):
            pass

        def send_initial_credentials(
            self,
            recipient_email,
            username,
            temporary_password,
        ):
            captured["recipient_email"] = recipient_email
            captured["username"] = username
            captured["temporary_password"] = temporary_password

    monkeypatch.setattr(
        employee_service,
        "EmailService",
        FakeEmailService,
    )

    employee_payload = {
        "active": True,
        "first_name": "Yemi",
        "last_name": "Permanent",
        "email": "yemi.permanent@example.com",
        "role": "manager",
        "hourly_rate": "20.00",
        "hire_date": "09/16/2026",
        "term_date": None,
    }

    create_response = client.post(
        "/employees",
        json=employee_payload,
        headers=manager_headers(),
    )

    assert create_response.status_code == 201

    username = captured["username"]
    temporary_password = captured["temporary_password"]

    assert username == "yemi.permanent"
    assert temporary_password

    # First login with the generated temporary password.
    first_login_response = client.post(
        "/auth/login",
        data={
            "username": username,
            "password": temporary_password,
        },
    )

    assert first_login_response.status_code == 200

    first_login_data = first_login_response.json()

    assert "access_token" in first_login_data
    assert first_login_data["must_change_password"] is True

    access_token = first_login_data["access_token"]

    # Change the temporary password to a permanent password.
    new_password = "Permanent123!"

    change_response = client.post(
        "/auth/password/change",
        json={
            "current_password": temporary_password,
            "new_password": new_password,
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        },
    )

    assert change_response.status_code == 200

    assert change_response.json() == {
        "message": "Password changed successfully"
    }

    db.expire_all()

    auth_record = (
        db.query(EmployeeAuth)
        .filter(
            EmployeeAuth.username == username
        )
        .first()
    )

    assert auth_record is not None
    assert auth_record.is_temporary_password is False

    # The employee can now log in with the permanent password.
    permanent_login_response = client.post(
        "/auth/login",
        data={
            "username": username,
            "password": new_password,
        },
    )

    assert permanent_login_response.status_code == 200

    permanent_login_data = permanent_login_response.json()

    assert "access_token" in permanent_login_data
    assert permanent_login_data["must_change_password"] is False

    # The old temporary password must no longer work.
    old_password_response = client.post(
        "/auth/login",
        data={
            "username": username,
            "password": temporary_password,
        },
    )

    assert old_password_response.status_code == 401
