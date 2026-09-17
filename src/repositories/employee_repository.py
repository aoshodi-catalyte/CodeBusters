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
from exceptions.employee_exceptions import (
    EmployeeEmailAlreadyExistsError,
    EmployeeAlreadyDeactivatedError,
)
from exceptions.secure_login_exceptions import EmployeeNotFoundError
from secure_login.secure_login_schema import EmployeeAuth
from utils.credential_generator import (
    generate_temporary_password,
    generate_username,
)
from utils.password_utils import hash_password


def map_role_enum_to_fk(
    enum_value: EmployeeRole | str,
    db: Session,
) -> int:
    """
    Map an EmployeeRole enum or string to its corresponding foreign key ID.
    """

    if isinstance(enum_value, EmployeeRole):
        role_str = enum_value.value
    else:
        role_str = enum_value

    role_row = (
        db.query(EmployeeRoleSchema)
        .filter_by(role=role_str)
        .first()
    )

    if not role_row:
        raise ValueError(
            f"EmployeeRole '{role_str}' not found "
            "in employee_role table"
        )

    return role_row.id


class EmployeeRepository:
    """
    Provides database operations for employee records, including creation,
    retrieval, and role foreign-key resolution.
    """

    def __init__(self, db: Session):
        self.db = db

    def create_new_employee(
        self,
        employee_data: Employee,
        return_credentials: bool = False,
    ):
        """
        Create a new employee and automatically generate login credentials.

        By default, returns only the created employee to preserve the
        existing repository interface.

        When return_credentials is True, returns a tuple containing:
            - the created employee
            - the generated username
            - the plaintext temporary password

        The plaintext temporary password is never stored in the database.
        Only its hash is persisted.
        """

        role_id = map_role_enum_to_fk(
            employee_data.role,
            self.db,
        )

        db_employee = EmployeeSchema(
            active=employee_data.active,
            first_name=employee_data.first_name.strip(),
            last_name=employee_data.last_name.strip(),
            email=employee_data.email,
            phone_number=employee_data.phone_number,
            role_id=role_id,
            hourly_rate=float(employee_data.hourly_rate),
            hire_date=employee_data.hire_date,
            term_date=employee_data.term_date,
        )

        self.db.add(db_employee)

        # Assign the employee ID before creating EmployeeAuth.
        self.db.flush()

        username = self._generate_unique_username(
            db_employee.first_name,
            db_employee.last_name,
        )

        temporary_password = generate_temporary_password()

        password_hash = hash_password(
            temporary_password
        )

        new_auth = EmployeeAuth(
            employee_id=db_employee.id,
            role=db_employee.role.role,
            username=username,
            password_hash=password_hash,
            is_temporary_password=True,
        )

        self.db.add(new_auth)

        self.db.commit()

        self.db.refresh(db_employee)

        if return_credentials:
            return (
                db_employee,
                username,
                temporary_password,
            )

        return db_employee

    def get_all_employees(self) -> list[EmployeeSchema]:
        """
        Retrieve all employee records from the database.

        Returns:
            A list of all employees. Returns an empty list when no
            employees exist.
        """

        return self.db.query(EmployeeSchema).all()

    def get_employee_by_id(
        self,
        employee_id: int,
    ) -> EmployeeSchema:
        """
        Retrieve an employee by its unique identifier.

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

    def _ensure_email_unique(
        self,
        email: str,
        exclude_id: int | None = None,
    ):
        """
        Ensure no other employee has the given email.
        """

        query = (
            self.db.query(EmployeeSchema)
            .filter(EmployeeSchema.email == email)
        )

        if exclude_id is not None:
            query = query.filter(
                EmployeeSchema.id != exclude_id
            )

        if query.first():
            raise EmployeeEmailAlreadyExistsError(email)

    def update_employee(
        self,
        employee_id: int,
        employee_data: Employee,
    ) -> EmployeeSchema:
        """
        Update an existing employee with validated replacement data.

        Steps:
            - Fetch the employee.
            - Ensure the updated email is unique.
            - Map the EmployeeRole enum to its role ID.
            - Apply the updated fields.
            - Commit and refresh the record.
        """

        db_employee = self.get_employee_by_id(
            employee_id
        )

        if db_employee is None:
            raise EmployeeNotFoundError(
                employee_id
            )

        self._ensure_email_unique(
            employee_data.email,
            exclude_id=employee_id,
        )

        role_id = map_role_enum_to_fk(
            employee_data.role,
            self.db,
        )

        db_employee.active = employee_data.active
        db_employee.first_name = (
            employee_data.first_name
        )
        db_employee.last_name = (
            employee_data.last_name
        )
        db_employee.email = employee_data.email
        db_employee.phone_number = (
            employee_data.phone_number
        )
        db_employee.role_id = role_id
        db_employee.hourly_rate = (
            employee_data.hourly_rate
        )
        db_employee.hire_date = (
            employee_data.hire_date
        )
        db_employee.term_date = (
            employee_data.term_date
        )

        try:
            self.db.commit()
            self.db.refresh(db_employee)

        except IntegrityError as exc:
            self.db.rollback()

            raise EmployeeEmailAlreadyExistsError(
                employee_data.email
            ) from exc

        return db_employee

    def _generate_unique_username(
        self,
        first_name: str,
        last_name: str,
    ) -> str:
        """
        Generate a username that does not already exist.
        """

        base_username = generate_username(
            first_name,
            last_name,
        )

        username = base_username
        counter = 1

        while (
            self.db.query(EmployeeAuth)
            .filter(
                EmployeeAuth.username == username
            )
            .first()
            is not None
        ):
            username = f"{base_username}{counter}"
            counter += 1

        return username

    def deactivate_employee(
        self,
        employee_id: int,
    ):
        """
        Deactivate an employee by setting active to False.

        The employee record is preserved for historical purposes.
        """

        employee = self.get_employee_by_id(
            employee_id
        )

        if employee is None:
            raise EmployeeNotFoundError(
                employee_id
            )

        if employee.active is False:
            raise EmployeeAlreadyDeactivatedError(
                employee_id
            )

        employee.active = False

        self.db.commit()
        self.db.refresh(employee)

        return employee
