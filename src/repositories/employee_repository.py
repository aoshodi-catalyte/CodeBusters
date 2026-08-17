from sqlalchemy.orm import Session

from constants.EMPLOYEE_ROLES import EmployeeRole
from employee.employee_model import Employee
from employee.employee_schema import EmployeeSchema
from employee.employee_role_schema import EmployeeRoleSchema


def map_role_enum_to_fk(enum_value: EmployeeRole, db: Session) -> int:
    """
    Map an EmployeeRole enum to its corresponding foreign key ID in the database.
    """
    role_row = (
        db.query(EmployeeRoleSchema)
        .filter_by(role=enum_value.value)
        .first()
    )

    if not role_row:
        raise ValueError(f"EmployeeRole '{enum_value.value}' not found in employee_role table")

    return role_row.id

class EmployeeRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_new_employee(self, employee_data: Employee) -> EmployeeSchema:

        role_id = map_role_enum_to_fk(employee_data.role, self.db)

        db_employee = EmployeeSchema(
            active=employee_data.active,
            first_name=employee_data.first_name,
            last_name=employee_data.last_name,
            email=employee_data.email,
            role_id=role_id,
            hourly_rate=employee_data.hourly_rate,
            hire_date=employee_data.hire_date,
            term_date=employee_data.term_date
        )

        self.db.add(db_employee)
        self.db.commit()
        self.db.refresh(db_employee)

        return db_employee