from pydantic import ValidationError
import pytest
from employee.employee_model import Employee
from constants.employee_roles import EmployeeRole
from datetime import date


def test_employee_create():
    employee = Employee(
        active=True,
        first_name="John",
        last_name="Doe",
        email="johndoe@deer.com",
        role="manager",
        hourly_rate=19.00,
        hire_date="01/01/2023",
    )
    assert employee.active is True
    assert employee.first_name == "John"
    assert employee.last_name == "Doe"
    assert employee.email == "johndoe@deer.com"
    assert employee.role == EmployeeRole.MANAGER
    assert employee.hourly_rate == 19.00
    assert employee.hire_date == date(2023, 1, 1)


def test_employee_first_name_whitespace():
    employee = Employee(
        active=True,
        first_name=" John ",
        last_name="Doe",
        email="johndoe@deer.com",
        role="manager",
        hourly_rate=19.00,
        hire_date="01/01/2023",
    )
    assert employee.active is True
    assert employee.first_name == "John"
    assert employee.last_name == "Doe"
    assert employee.email == "johndoe@deer.com"
    assert employee.role == EmployeeRole.MANAGER
    assert employee.hourly_rate == 19.00
    assert employee.hire_date == date(2023, 1, 1)


def test_employee_last_name_whitespace():
    employee = Employee(
        active=True,
        first_name="John",
        last_name=" Doe ",
        email="johndoe@deer.com",
        role="manager",
        hourly_rate=19.00,
        hire_date="01/01/2023",
    )
    assert employee.active is True
    assert employee.first_name == "John"
    assert employee.last_name == "Doe"
    assert employee.email == "johndoe@deer.com"
    assert employee.role == EmployeeRole.MANAGER
    assert employee.hourly_rate == 19.00
    assert employee.hire_date == date(2023, 1, 1)


def test_employee_first_name_too_long():
    with pytest.raises(ValidationError):
        Employee(
            active=True,
            first_name="J" * 51,
            last_name="Doe",
            email="johndoe@deer.com",
        )


def test_employee_last_name_too_long():
    with pytest.raises(ValidationError):
        Employee(
            active=True,
            first_name="John",
            last_name="D" * 51,
            email="johndoe@deer.com",
        )


def test_employee_email_invalid():
    with pytest.raises(ValidationError):
        Employee(
            active=True,
            first_name="John",
            last_name="Doe",
            email="johndoedeer.com",
        )


def test_employee_email_invalid_domain():
    with pytest.raises(ValidationError):
        Employee(
            active=True,
            first_name="John",
            last_name="Doe",
            email="johndoe@",
        )


def test_employee_email_whitespace():
    with pytest.raises(ValidationError):
        Employee(
            active=True,
            first_name="John",
            last_name="Doe",
            email=" johndoedeer.com ",
        )


def test_employee_role_admin():
    employee = Employee(
        active=True,
        first_name="John",
        last_name="Doe",
        email="johndoe@deer.com",
        role="aDmin",
        hourly_rate=19.00,
        hire_date="01/01/2023",
    )
    assert employee.role == EmployeeRole.ADMIN


def test_employee_role_employee():
    employee = Employee(
        active=True,
        first_name="John",
        last_name="Doe",
        email="johndoe@deer.com",
        role="EMPLOYEE",
        hourly_rate=19.00,
        hire_date="01/01/2023",
    )
    assert employee.role == EmployeeRole.EMPLOYEE


def test_employee_role_invalid_role():
    with pytest.raises(ValidationError):
        Employee(
            active=True,
            first_name="John",
            last_name="Doe",
            email="johndoe@deer.com",
            role="Boss",
        )


def test_hourly_rate_negative():
    with pytest.raises(ValidationError):
        Employee(
            active=True,
            first_name="John",
            last_name="Doe",
            email="johndoe@deer.com",
            role="aDmin",
            hourly_rate=-19.00,
            hire_date="01/01/2023",
        )


def test_hourly_rate_zero_value():
    with pytest.raises(ValidationError):
        Employee(
            active=True,
            first_name="John",
            last_name="Doe",
            email="johndoe@deer.com",
            role="aDmin",
            hourly_rate=0,
            hire_date="01/01/2023",
        )


def test_hourly_rate_too_many_decimal_places():
    with pytest.raises(ValidationError):
        Employee(
            active=True,
            first_name="John",
            last_name="Doe",
            email="johndoe@deer.com",
            role="aDmin",
            hourly_rate="10.12345",
            hire_date="01/01/2023",
        )


def test_date_format_invalid():
    with pytest.raises(ValidationError):
        Employee(
            active=True,
            first_name="John",
            last_name="Doe",
            email="johndoe@deer.com",
            role="manager",
            hourly_rate=19.00,
            hire_date="01-01-2023",
        )


def test_date_hire_date_required():
    with pytest.raises(ValidationError):
        Employee(
            active=True,
            first_name="John",
            last_name="Doe",
            email="johndoe@deer.com",
            role="manager",
            hourly_rate=19.00,
        )


def test_employee_term_date_none():
    employee = Employee(
        active=True,
        first_name="John",
        last_name="Doe",
        email="johndoe@deer.com",
        role="manager",
        hourly_rate=19.00,
        hire_date="01/01/2023",
        term_date=None,
    )
    assert employee.active is True
    assert employee.first_name == "John"
    assert employee.last_name == "Doe"
    assert employee.email == "johndoe@deer.com"
    assert employee.role == EmployeeRole.MANAGER
    assert employee.hourly_rate == 19.00
    assert employee.hire_date == date(2023, 1, 1)
    assert employee.term_date == None


def test_active_employee_with_term_date():
    with pytest.raises(ValidationError):
        Employee(
            active=True,
            first_name="John",
            last_name="Doe",
            email="johndoe@deer.com",
            role="manager",
            hourly_rate=19.00,
            hire_date="01/01/2023",
            term_date="01/01/2023",
        )


def test_active_employee_with_term_date_before_hire_date():
    with pytest.raises(ValidationError):
        Employee(
            active=True,
            first_name="John",
            last_name="Doe",
            email="johndoe@deer.com",
            role="manager",
            hourly_rate=19.00,
            hire_date="01/01/2023",
            term_date="01/01/2021",
        )


def test_inactive_employee_with_no_term_date():
    with pytest.raises(ValidationError):
        Employee(
            active=False,
            first_name="John",
            last_name="Doe",
            email="johndoe@deer.com",
            role="manager",
            hourly_rate=19.00,
            hire_date="01/01/2023",
        )


def test_inactive_employee_with_term_date_past_today():
    with pytest.raises(ValidationError):
        Employee(
            active=False,
            first_name="John",
            last_name="Doe",
            email="johndoe@deer.com",
            role="manager",
            hourly_rate=19.00,
            hire_date="08/18/2026",
            term_date="09/01/2026",
        )
