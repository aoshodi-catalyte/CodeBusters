import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from constants.employee_roles import EmployeeRole
from employee.employee_model import Employee
from employee.employee_schema import EmployeeSchema, Base
from employee.employee_role_schema import EmployeeRoleSchema
from repositories.employee_repository import EmployeeRepository
from pydantic import ValidationError
from datetime import date, timedelta


def run_db():
    engine = create_engine("sqlite:///:memory:", echo=False)
    TestingSessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()

    role = EmployeeRoleSchema(role="manager")
    db.add(role)
    db.commit()
    db.refresh(role)

    repo = EmployeeRepository(db)

    return db, repo, role


def setup_db_empty_role_table():
    engine = create_engine("sqlite:///:memory:", echo=False)
    TestingSessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    repo = EmployeeRepository(db)
    return db, repo


def test_create_new_employee_success():
    db, repo, role = run_db()

    employee_model = Employee(
        active=True,
        first_name="John",
        last_name="Doe",
        email="john@doe.com",
        role=EmployeeRole.MANAGER,
        hourly_rate="10.50",
        hire_date="01/01/2023",
    )

    created = repo.create_new_employee(employee_model)

    assert isinstance(created, EmployeeSchema)
    assert created.id is not None
    assert created.first_name == "John"
    assert created.last_name == "Doe"
    assert created.email == "john@doe.com"
    assert created.hourly_rate == 10.50
    assert created.role_id == role.id
    assert created.active is True

    db.close()


def test_role_fk_lookup_success():
    db, repo, role_row = run_db()

    employee_model = Employee(
        active=True,
        first_name="John",
        last_name="Doe",
        email="john@doe.com",
        role=EmployeeRole.MANAGER,
        hourly_rate="10.50",
        hire_date="01/01/2023",
    )

    created = repo.create_new_employee(employee_model)

    assert created.role_id == role_row.id

    assert isinstance(created, EmployeeSchema)
    assert created.first_name == "John"
    assert created.last_name == "Doe"
    assert created.email == "john@doe.com"

    db.close()


def test_role_fk_lookup_failure():
    db, repo = setup_db_empty_role_table()

    employee_model = Employee(
        active=True,
        first_name="John",
        last_name="Doe",
        email="john@doe.com",
        role=EmployeeRole.MANAGER,
        hourly_rate="10.50",
        hire_date="01/01/2023",
    )

    db.close()
    with pytest.raises(ValueError):
        repo.create_new_employee(employee_model)


def test_term_date_validation_propagates_to_repository():
    future_date = (date.today() + timedelta(days=3)).strftime("%m/%d/%Y")

    with pytest.raises(ValidationError):
        Employee(
            active=False,
            first_name="John",
            last_name="Doe",
            email="john@doe.com",
            role=EmployeeRole.MANAGER,
            hourly_rate="10.50",
            hire_date="01/01/2023",
            term_date=future_date,
        )


def test_repository_does_not_mutate_input():
    db, repo, role_row = run_db()

    employee_model = Employee(
        active=True,
        first_name="  John  ",
        last_name="  Doe  ",
        email="john@doe.com",
        role=EmployeeRole.MANAGER,
        hourly_rate="10.50",
        hire_date="01/01/2023",
    )

    original_data = employee_model.model_dump()

    repo.create_new_employee(employee_model)

    assert employee_model.model_dump() == original_data
    db.close()


def test_repository_stores_trimmed_fields():
    db, repo, role_row = run_db()

    employee_model = Employee(
        active=True,
        first_name="  John  ",
        last_name="  Doe  ",
        email="john@doe.com",
        role=EmployeeRole.MANAGER,
        hourly_rate="10.50",
        hire_date="01/01/2023",
    )

    created = repo.create_new_employee(employee_model)

    assert created.first_name == "John"
    assert created.last_name == "Doe"
