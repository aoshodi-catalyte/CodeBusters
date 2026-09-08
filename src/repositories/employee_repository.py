"""
Repository layer for employee-related database operations, including creation,
retrieval, and role mapping logic.
"""

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from constants.employee_roles import EmployeeRole
from employee.employee_model import Employee
from employee.employee_schema import EmployeeSchema
from employee.employee_role_schema import EmployeeRoleSchema
from exceptions.employee_exceptions import EmployeeEmailAlreadyExistsError
from exceptions.secure_login_exceptions import EmployeeNotFoundError
from utils.error_utils import parse_integrity_error


def map_role_enum_to_fk(enum_value: EmployeeRole | str, db: Session) -> int:
    """
    Map an EmployeeRole enum or string to its corresponding foreign key ID.
    """

    # Normalize input
    if isinstance(enum_value, EmployeeRole):
        role_str = enum_value.value
    else:
        role_str = enum_value

    role_row = db.query(EmployeeRoleSchema).filter_by(role=role_str).first()

    if not role_row:
        raise ValueError(
            f"EmployeeRole '{role_str}' not found in employee_role table")

    return role_row.id


class EmployeeRepository:
    """
    Provides database operations for employee records, including creation,
    retrieval, and role foreign-key resolution.
    """

    def __init__(self, db: Session):
        self.db = db

    def create_new_employee(self, employee_data: Employee) -> EmployeeSchema:
        """
        Create a new employee record in the database.
        """

        role_id = map_role_enum_to_fk(employee_data.role, self.db)

        db_employee = EmployeeSchema(
            active=employee_data.active,
            first_name=employee_data.first_name.strip(),
            last_name=employee_data.last_name.strip(),
            email=employee_data.email,
            role_id=role_id,
            hourly_rate=float(employee_data.hourly_rate),
            hire_date=employee_data.hire_date,
            term_date=employee_data.term_date,
        )

        self.db.add(db_employee)
        self.db.commit()
        self.db.refresh(db_employee)

        return db_employee

    def get_all_employees(self) -> list[EmployeeSchema]:
        """
        Retrieve all employee records from the database.

        Returns:
            list[EmployeeSchema]: A list of all employees. Returns an
                empty list if no employees exist.
        """
        return self.db.query(EmployeeSchema).all()

    def get_employee_by_id(self, employee_id: int) -> EmployeeSchema:
        """Retrieve an employee by its unique ID.

        Args:
            employee_id: The unique identifier of the employee.

        Returns:
            The requested employee.

        Raises:
            EmployeeNotFoundError:
                If the employee does not exist.
        """
        employee = (
            self.db.query(EmployeeSchema)
            .filter(EmployeeSchema.id == employee_id)
            .first()
        )

        if employee is None:
            raise EmployeeNotFoundError(employee_id)

        return employee

    def update_employee(
        self,
        employee_id: int,
        employee: Employee
    ) -> EmployeeSchema:
        """
        Update and persist an existing employee's properties.

        Args:
            employee_id: The ID of the employee to update.
            employee: Employee object containing the validated
                replacement employee data.

        Returns:
            EmployeeSchema: The updated employee record.

        Raises:
            EmployeeNotFoundError:
                If no employee exists with the given ID.
            EmployeeEmailAlreadyExistsError:
                If another employee already has the given email.
        """
        db_employee = self.get_employee_by_id(employee_id)
        if db_employee is None:
            raise EmployeeNotFoundError(employee_id)

        existing_email = self.get_employee_by_email(employee.email)
        if existing_email and existing_email.id != employee_id:
            raise EmployeeEmailAlreadyExistsError(employee.email)

        db_employee.active = employee.active
        db_employee.first_name = employee.first_name
        db_employee.last_name = employee.last_name
        db_employee.email = employee.email
        db_employee.role = employee.role
        db_employee.hourly_rate = employee.hourly_rate
        db_employee.hire_date = employee.hire_date
        db_employee.term_date = employee.term_date

        try:
            self.db.commit()
            self.db.refresh(db_employee)
        except IntegrityError as exc:
            self.db.rollback()
            constraint, error_message = parse_integrity_error(exc)

            if "email" in error_message:
                raise EmployeeEmailAlreadyExistsError(
                    employee.email
                ) from exc

        return db_employee
