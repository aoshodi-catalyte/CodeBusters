"""
Repository layer for employee-related database operations, including creation
and role mapping logic.
"""

from sqlalchemy.orm import Session
from constants.employee_roles import EmployeeRole
from employee.employee_model import Employee
from employee.employee_schema import EmployeeSchema
from employee.employee_role_schema import EmployeeRoleSchema


def map_role_enum_to_fk(enum_value: EmployeeRole, db: Session) -> int:
    """
    Map an EmployeeRole enum to its corresponding foreign key ID in the database.
    """
    role_row = db.query(EmployeeRoleSchema).filter_by(role=enum_value.value).first()

    if not role_row:
        raise ValueError(
            f"EmployeeRole '{enum_value.value}' not found in employee_role table"
        )

    return role_row.id


class EmployeeRepository:
    """
    Provides database operations for employee records, including creation and
    role foreign-key resolution.
    """

    def __init__(self, db: Session):
        self.db = db

    def create_new_employee(self, employee_data: Employee) -> EmployeeSchema:
        """
        Create a new employee record in the database.

        This method:
            - Resolves the employee role enum to its foreign key ID.
            - Constructs an EmployeeSchema ORM instance.
            - Persists the new employee to the database.
            - Returns the refreshed ORM object.

        Args:
            employee_data (Employee):
                Validated Pydantic model containing employee fields.

        Returns:
            EmployeeSchema:
                The newly created and persisted employee ORM instance.

        Raises:
            ValueError:
                If the provided role cannot be mapped to a valid role ID.
        """

        role_id = map_role_enum_to_fk(employee_data.role, self.db)

        db_employee = EmployeeSchema(
            active=employee_data.active,
            first_name=employee_data.first_name,
            last_name=employee_data.last_name,
            email=employee_data.email,
            role_id=role_id,
            hourly_rate=employee_data.hourly_rate,
            hire_date=employee_data.hire_date,
            term_date=employee_data.term_date,
        )

        self.db.add(db_employee)
        self.db.commit()
        self.db.refresh(db_employee)

        return db_employee