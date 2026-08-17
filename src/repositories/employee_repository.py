from sqlalchemy.orm import Session

from constants.EMPLOYEE_ROLES import EmployeeRole
from employee.employee_model import Employee
from employee.employee_schema import EmployeeSchema
from employee.employee_role_schema import EmployeeRoleSchema


class EmployeeRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_new_employee(self, employee_data: Employee) -> EmployeeSchema:

        role_name = employee_data.role.value

        role_row = (
            self.db.query(EmployeeRoleSchema)
            .filter(EmployeeRoleSchema.role == role_name)
            .first()
        )

        if role_row is None:
            raise ValueError(f"Employee role '{role_name}' does not exist")

        db_employee = EmployeeSchema(
            active=employee_data.active,
            first_name=employee_data.first_name,
            last_name=employee_data.last_name,
            email=employee_data.email,
            role_id=role_row.id,
            hourly_rate=employee_data.hourly_rate,
            hire_date=employee_data.hire_date,
            term_date=employee_data.term_date
        )

        self.db.add(db_employee)
        self.db.commit()
        self.db.refresh(db_employee)

        return db_employee