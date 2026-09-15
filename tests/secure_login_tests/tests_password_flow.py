"""
Integration tests for the temporary-to-permanent password lifecycle.
"""

# pylint: disable=duplicate-code

from employee.employee_model import Employee
from constants.employee_roles import EmployeeRole
from repositories.employee_repository import EmployeeRepository
from secure_login.secure_login_schema import EmployeeAuth
from utils.password_utils import verify_password


def _login(client, username, password):
    """Log in and return the JSON response."""
    response = client.post(
        "/auth/login",
        data={
            "username": username,
            "password": password,
        },
    )
    return response


def test_temporary_password_to_permanent_password_flow(
    db,
    client,
    monkeypatch,
):
    """
    Verify the complete temporary-to-permanent password lifecycle.
    """

    passwords = {
        "temporary": "Temporary123!",
        "permanent": "Permanent123!",
    }

    monkeypatch.setattr(
        "repositories.employee_repository.generate_temporary_password",
        lambda: passwords["temporary"],
    )

    employee_data = Employee(
        active=True,
        first_name="John",
        last_name="Smith",
        email="john@example.com",
        role=EmployeeRole.MANAGER,
        hourly_rate=20.00,
        hire_date="09/10/2026",
    )

    repo = EmployeeRepository(db)
    employee = repo.create_new_employee(employee_data)

    auth = (
        db.query(EmployeeAuth)
        .filter(
            EmployeeAuth.employee_id == employee.id
        )
        .first()
    )

    assert auth is not None
    assert auth.username == "john.smith"

    assert auth.password_hash != passwords["temporary"]

    assert verify_password(
        passwords["temporary"],
        auth.password_hash,
    )

    assert auth.is_temporary_password is True

    original_password_hash = auth.password_hash

    # ---------------------------------------------------------
    # Temporary password login
    # ---------------------------------------------------------

    login_response = _login(
        client,
        "john.smith",
        passwords["temporary"],
    )

    assert login_response.status_code == 200

    login_data = login_response.json()

    assert "access_token" in login_data
    assert login_data["token_type"] == "bearer"
    assert login_data["must_change_password"] is True

    # ---------------------------------------------------------
    # Change temporary password
    # ---------------------------------------------------------

    change_response = client.post(
        "/auth/password/change",
        headers={
            "Authorization": (
                f"Bearer {login_data['access_token']}"
            ),
        },
        json={
            "current_password": passwords["temporary"],
            "new_password": passwords["permanent"],
        },
    )

    assert change_response.status_code == 200

    assert change_response.json() == {
        "message": "Password changed successfully"
    }

    # ---------------------------------------------------------
    # Verify database was updated
    # ---------------------------------------------------------

    db.expire_all()

    updated_auth = (
        db.query(EmployeeAuth)
        .filter(
            EmployeeAuth.employee_id == employee.id
        )
        .first()
    )

    assert updated_auth is not None
    assert updated_auth.is_temporary_password is False
    assert updated_auth.password_hash != original_password_hash

    assert verify_password(
        passwords["permanent"],
        updated_auth.password_hash,
    )

    assert not verify_password(
        passwords["temporary"],
        updated_auth.password_hash,
    )

    # ---------------------------------------------------------
    # Old password must fail
    # ---------------------------------------------------------

    old_password_response = _login(
        client,
        "john.smith",
        passwords["temporary"],
    )

    assert old_password_response.status_code == 401

    # ---------------------------------------------------------
    # New password must work
    # ---------------------------------------------------------

    new_password_response = _login(
        client,
        "john.smith",
        passwords["permanent"],
    )

    assert new_password_response.status_code == 200

    assert "access_token" in new_password_response.json()
    assert (
        new_password_response.json()["token_type"]
        == "bearer"
    )
    assert (
        new_password_response.json()["must_change_password"]
        is False
    )
