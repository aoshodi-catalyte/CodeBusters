import pytest
from pydantic import ValidationError

from secure_login.secure_login_model import EmployeeAuthCreate


def test_username_whitespace_only():
    with pytest.raises(ValidationError):
        EmployeeAuthCreate(employee_id=1, username="   ", password="password123")


def test_password_whitespace_only():
    with pytest.raises(ValidationError):
        EmployeeAuthCreate(employee_id=1, username="testuser", password="   ")


def test_non_string_username():
    with pytest.raises(ValidationError):
        EmployeeAuthCreate(employee_id=1, username=12345, password="password123")


def test_non_string_password():
    with pytest.raises(ValidationError):
        EmployeeAuthCreate(employee_id=1, username="testuser", password=99999)


def test_negative_employee_id():
    with pytest.raises(ValidationError):
        EmployeeAuthCreate(employee_id=-1, username="testuser", password="password123")


def test_zero_employee_id():
    with pytest.raises(ValidationError):
        EmployeeAuthCreate(employee_id=0, username="testuser", password="password123")


def test_extremely_long_username():
    long_username = "x" * 500
    data = EmployeeAuthCreate(
        employee_id=1, username=long_username, password="password123"
    )
    assert data.username == long_username
