from employee.employee_model import Employee
from constants.employee_roles import EmployeeRole
from repositories.employee_repository import EmployeeRepository
from secure_login.secure_login_schema import EmployeeAuth
from utils.password_utils import verify_password


def test_temporary_password_to_permanent_password_flow(
    db,
    client,
    monkeypatch,
):
    """
    Verify the complete Phase 2 password lifecycle:

    1. Create an employee.
    2. Generate temporary credentials.
    3. Confirm the temporary password is hashed.
    4. Log in with the temporary password.
    5. Confirm the login requires a password change.
    6. Change the password.
    7. Confirm the temporary flag is cleared.
    8. Confirm the old password no longer works.
    9. Confirm the new password works.
    """

    temporary_password = "Temporary123!"

    permanent_password = "Permanent123!"

    # Use a known temporary password for the test.
    # Production code still generates a secure random password.
    monkeypatch.setattr(
        "repositories.employee_repository.generate_temporary_password",
        lambda: temporary_password,
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

    # ---------------------------------------------------------
    # Step 1: Verify EmployeeAuth was created.
    # ---------------------------------------------------------

    auth = (
        db.query(EmployeeAuth)
        .filter(
            EmployeeAuth.employee_id == employee.id
        )
        .first()
    )

    assert auth is not None
    assert auth.username == "john.smith"

    # ---------------------------------------------------------
    # Step 2: Verify the password was hashed.
    # ---------------------------------------------------------

    assert auth.password_hash != temporary_password

    assert verify_password(
        temporary_password,
        auth.password_hash,
    )

    # ---------------------------------------------------------
    # Step 3: Verify this is still a temporary password.
    # ---------------------------------------------------------

    assert auth.is_temporary_password is True

    # Save the original hash so we can prove it changes later.
    original_password_hash = auth.password_hash

    # ---------------------------------------------------------
    # Step 4: Log in using the generated credentials.
    # ---------------------------------------------------------

    login_response = client.post(
        "/auth/login",
        data={
            "username": "john.smith",
            "password": temporary_password,
        },
    )

    assert login_response.status_code == 200

    login_data = login_response.json()

    assert "access_token" in login_data
    assert login_data["token_type"] == "bearer"

    # ---------------------------------------------------------
    # Step 5: First login must require a password change.
    # ---------------------------------------------------------

    assert login_data["must_change_password"] is True

    access_token = login_data["access_token"]

    # ---------------------------------------------------------
    # Step 6: Change the temporary password.
    # ---------------------------------------------------------

    change_response = client.post(
        "/auth/password/change",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
        json={
            "current_password": temporary_password,
            "new_password": permanent_password,
        },
    )

    assert change_response.status_code == 200

    assert change_response.json() == {
        "message": "Password changed successfully"
    }

    # ---------------------------------------------------------
    # Step 7: Reload EmployeeAuth from the database.
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

    # Temporary flag must now be false.
    assert updated_auth.is_temporary_password is False

    # The password hash must have changed.
    assert updated_auth.password_hash != original_password_hash

    # The new password must match the new bcrypt hash.
    assert verify_password(
        permanent_password,
        updated_auth.password_hash,
    )

    # The old password must no longer match.
    assert not verify_password(
        temporary_password,
        updated_auth.password_hash,
    )

    # ---------------------------------------------------------
    # Step 8: Old password should no longer allow login.
    # ---------------------------------------------------------

    old_password_response = client.post(
        "/auth/login",
        data={
            "username": "john.smith",
            "password": temporary_password,
        },
    )

    assert old_password_response.status_code == 401

    # ---------------------------------------------------------
    # Step 9: New password should allow login.
    # ---------------------------------------------------------

    new_password_response = client.post(
        "/auth/login",
        data={
            "username": "john.smith",
            "password": permanent_password,
        },
    )

    assert new_password_response.status_code == 200

    new_login_data = new_password_response.json()

    assert "access_token" in new_login_data
    assert new_login_data["token_type"] == "bearer"

    # ---------------------------------------------------------
    # Step 10: Permanent password no longer requires a change.
    # ---------------------------------------------------------

    assert new_login_data["must_change_password"] is False

