from datetime import date

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from database import Base
from employee.employee_role_schema import EmployeeRoleSchema
from employee.employee_schema import EmployeeSchema
from secure_login.secure_login_schema import EmployeeAuth


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}
    )

    with engine.connect() as conn:
        conn.execute(text("PRAGMA foreign_keys=ON"))

    Base.metadata.create_all(engine)

    TestingSessionLocal = sessionmaker(bind=engine)
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)


@pytest.fixture()
def employee(db_session):
    role = EmployeeRoleSchema(id=1, role="cashier")
    db_session.add(role)
    db_session.flush()

    emp = EmployeeSchema(
        active=True,
        first_name="Test",
        last_name="Employee",
        email="test@example.com",
        role_id=1,
        hourly_rate=20.0,
        hire_date=date.today(),
    )
    db_session.add(emp)
    db_session.commit()
    db_session.refresh(emp)
    return emp


def make_auth(employee_id, **overrides):
    defaults = dict(
        employee_id=employee_id,
        role="cashier",
        username="testuser",
        password_hash="hashed_value",
    )
    defaults.update(overrides)
    return EmployeeAuth(**defaults)


class TestEmployeeAuthCreation:
    def test_creates_record_with_valid_data(self, db_session, employee):
        auth = make_auth(employee.id)
        db_session.add(auth)
        db_session.commit()
        db_session.refresh(auth)

        assert auth.id is not None
        assert auth.employee_id == employee.id
        assert auth.role == "cashier"
        assert auth.username == "testuser"
        assert auth.password_hash == "hashed_value"

    def test_relationship_returns_associated_employee(self, db_session, employee):
        auth = make_auth(employee.id)
        db_session.add(auth)
        db_session.commit()
        db_session.refresh(auth)

        assert auth.employee.id == employee.id


class TestEmployeeAuthConstraints:
    def test_username_must_be_unique(self, db_session, employee):
        db_session.add(make_auth(employee.id, username="dupe"))
        db_session.commit()

        db_session.add(make_auth(employee.id, username="dupe"))
        with pytest.raises(IntegrityError):
            db_session.commit()

    @pytest.mark.parametrize(
        "field",
        ["employee_id", "role", "username", "password_hash"],
    )
    def test_required_fields_cannot_be_null(self, db_session, employee, field):
        kwargs = dict(
            employee_id=employee.id,
            role="cashier",
            username="uniqueuser",
            password_hash="hashed_value",
        )
        kwargs[field] = None
        db_session.add(EmployeeAuth(**kwargs))

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_foreign_key_rejects_nonexistent_employee(self, db_session):
        auth = make_auth(employee_id=999999)
        db_session.add(auth)
        with pytest.raises(IntegrityError):
            db_session.commit()
