import pytest
from pydantic import ValidationError

from secure_login.secure_login_model import EmployeeAuthCreate


def test_valid_employee_auth_create():
    data = EmployeeAuthCreate(
        employee_id=1,
        username="testuser",
        password="ValidPassword12",
    )

    assert data.employee_id == 1
    assert data.username == "testuser"
    assert data.password == "ValidPassword12"


def test_missing_employee_id():
    with pytest.raises(ValidationError):
        EmployeeAuthCreate(
            username="testuser",
            password="Password1234",
        )


def test_missing_username():
    with pytest.raises(ValidationError):
        EmployeeAuthCreate(
            employee_id=1,
            password="Password1234",
        )


def test_missing_password():
    with pytest.raises(ValidationError):
        EmployeeAuthCreate(
            employee_id=1,
            username="testuser",
        )


def test_password_too_long():
    long_password = "A" + ("a" * 71) + "1"

    assert len(long_password) == 73

    with pytest.raises(ValidationError):
        EmployeeAuthCreate(
            employee_id=1,
            username="testuser",
            password=long_password,
        )


def test_password_max_length_boundary():
    valid_password = "A" + ("a" * 70) + "1"

    assert len(valid_password) == 72

    data = EmployeeAuthCreate(
        employee_id=1,
        username="testuser",
        password=valid_password,
    )

    assert data.password == valid_password


def test_invalid_employee_id_type():
    with pytest.raises(ValidationError):
        EmployeeAuthCreate(
            employee_id="not-an-int",
            username="testuser",
            password="Password1234",
        )
