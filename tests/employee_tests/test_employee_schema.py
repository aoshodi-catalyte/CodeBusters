from sqlalchemy import Integer, String, Float, Boolean, Date
from employee.employee_schema import EmployeeSchema
from employee.employee_role_schema import EmployeeRoleSchema
from secure_login.secure_login_schema import EmployeeAuth


def test_employee_table_name():
    assert EmployeeSchema.__tablename__ == "employee"


def test_employee_columns_exist():
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


def test_employee_column_types():
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


def test_employee_primary_key():
    pk = EmployeeSchema.__table__.primary_key.columns
    assert "id" in pk


def test_employee_nullable_constraints():
    columns = EmployeeSchema.__table__.columns

    assert columns["first_name"].nullable is False
    assert columns["last_name"].nullable is False
    assert columns["email"].nullable is False
    assert columns["role_id"].nullable is False
    assert columns["hourly_rate"].nullable is False
    assert columns["hire_date"].nullable is False
    assert columns["term_date"].nullable is True


def test_employee_relationships():
    relationships = EmployeeSchema.__mapper__.relationships

    assert "role" in relationships
    role_rel = relationships["role"]
    assert role_rel.mapper.class_.__name__ == "EmployeeRoleSchema"
    assert role_rel.back_populates == "employees"

    assert "auth" in relationships
    auth_rel = relationships["auth"]
    assert auth_rel.mapper.class_.__name__ == "EmployeeAuth"
    assert auth_rel.back_populates == "employee"


def test_auth_table_name():
    assert EmployeeAuth.__tablename__ == "employee_auth"


def test_auth_columns_exist():
    columns = EmployeeAuth.__table__.columns

    assert "id" in columns
    assert "employee_id" in columns
    assert "role" in columns
    assert "username" in columns
    assert "password_hash" in columns


def test_auth_column_types():
    columns = EmployeeAuth.__table__.columns

    assert isinstance(columns["id"].type, Integer)
    assert isinstance(columns["employee_id"].type, Integer)
    assert isinstance(columns["role"].type, String)
    assert isinstance(columns["username"].type, String)
    assert isinstance(columns["password_hash"].type, String)


def test_auth_primary_key():
    pk = EmployeeAuth.__table__.primary_key.columns
    assert "id" in pk


def test_auth_nullable_constraints():
    columns = EmployeeAuth.__table__.columns

    assert columns["employee_id"].nullable is False
    assert columns["role"].nullable is False
    assert columns["username"].nullable is False
    assert columns["password_hash"].nullable is False


def test_auth_relationships():
    relationships = EmployeeAuth.__mapper__.relationships

    assert "employee" in relationships
    rel = relationships["employee"]

    assert rel.mapper.class_.__name__ == "EmployeeSchema"
    assert rel.back_populates == "auth"
