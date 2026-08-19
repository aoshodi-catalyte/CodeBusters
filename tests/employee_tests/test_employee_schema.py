from sqlalchemy import Integer, String, Float, Boolean, Date
from employee.employee_schema import EmployeeSchema
from employee.employee_role_schema import EmployeeRoleSchema


def test_table_name():
    assert EmployeeSchema.__tablename__ == "employee"


def test_columns_exist():
    columns = EmployeeSchema.__table__.columns

    assert "id" in columns
    assert "active" in columns
    assert "first_name" in columns
    assert "last_name" in columns
    assert "email" in columns
    assert "role_id" in columns
    assert "hourly_rate" in columns
    assert "hire_date" in columns
    assert "term_date" in columns


def test_column_types():
    columns = EmployeeSchema.__table__.columns

    assert isinstance(columns["id"].type, Integer)
    assert isinstance(columns["active"].type, Boolean)
    assert isinstance(columns["first_name"].type, String)
    assert isinstance(columns["last_name"].type, String)
    assert isinstance(columns["email"].type, String)
    assert isinstance(columns["role_id"].type, Integer)
    assert isinstance(columns["hourly_rate"].type, Float)
    assert isinstance(columns["hire_date"].type, Date)
    assert isinstance(columns["term_date"].type, Date)


def test_primary_key():
    pk = EmployeeSchema.__table__.primary_key.columns
    assert "id" in pk


def test_nullable_constraints():
    columns = EmployeeSchema.__table__.columns

    assert columns["first_name"].nullable is False
    assert columns["last_name"].nullable is False
    assert columns["email"].nullable is False
    assert columns["role_id"].nullable is False

    assert columns["hourly_rate"].nullable is False
    assert columns["hire_date"].nullable is False
    assert columns["term_date"].nullable is True


def test_relationship_exists():
    relationships = EmployeeSchema.__mapper__.relationships

    assert "role" in relationships

    rel = relationships["role"]

    assert rel.mapper.class_.__name__ == "EmployeeRoleSchema"

    assert rel.back_populates == "employees"
