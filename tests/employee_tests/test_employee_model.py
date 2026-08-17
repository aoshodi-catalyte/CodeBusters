from employee.employee_model import Employee
from constants.EMPLOYEE_ROLES import EmployeeRole
from datetime import date

def test_employee_model():
    employee = Employee(
        active=True,
        first_name="John",
        last_name="Doe",
        email="johndoe@deer.com",
        role="manager",
        hourly_rate=19.00,
        hire_date="01/01/2023"
    )
    assert employee.active is True
    assert employee.first_name == "John"
    assert employee.last_name == "Doe"
    assert employee.email == "johndoe@deer.com"
    assert employee.role == EmployeeRole.MANAGER
    assert employee.hourly_rate == 19.00
    assert employee.hire_date == date(2023, 1, 1)