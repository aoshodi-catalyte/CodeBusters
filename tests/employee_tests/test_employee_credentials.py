from repositories.employee_repository import EmployeeRepository
from secure_login.secure_login_schema import EmployeeAuth
from employee.employee_model import Employee
from constants.employee_roles import EmployeeRole

def test_new_employee_creates_auth_credentials(db):
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

    employee = repo.create_new_employee(
        employee_data
    )

    auth = (
        db.query(EmployeeAuth)
        .filter(
            EmployeeAuth.employee_id == employee.id
        )
        .first()
    )

    assert auth is not None
    assert auth.username == "john.smith"
    assert auth.password_hash is not None
    assert auth.is_temporary_password is True

def test_duplicate_employee_names_generate_unique_usernames(db):
    first_employee = Employee(
        active=True,
        first_name="John",
        last_name="Smith",
        email="john1@example.com",
        role=EmployeeRole.MANAGER,
        hourly_rate=20.00,
        hire_date="09/10/2026",
    )

    second_employee = Employee(
        active=True,
        first_name="John",
        last_name="Smith",
        email="john2@example.com",
        role=EmployeeRole.MANAGER,
        hourly_rate=20.00,
        hire_date="09/10/2026",
    )

    repo = EmployeeRepository(db)

    employee_one = repo.create_new_employee(
        first_employee
    )

    employee_two = repo.create_new_employee(
        second_employee
    )

    auth_one = (
        db.query(EmployeeAuth)
        .filter(
            EmployeeAuth.employee_id == employee_one.id
        )
        .first()
    )

    auth_two = (
        db.query(EmployeeAuth)
        .filter(
            EmployeeAuth.employee_id == employee_two.id
        )
        .first()
    )

    assert auth_one.username == "john.smith"
    assert auth_two.username == "john.smith1"