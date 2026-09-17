"""
Application service for employee creation and credential delivery.
"""

# pylint: disable=unused-argument

from config import settings
from employee.employee_model import Employee
from employee.employee_schema import EmployeeSchema
from repositories.employee_repository import EmployeeRepository
from services.email_service import EmailService


class EmployeeService:
    """
    Coordinates employee creation and initial credential delivery.
    """

    def __init__(
        self,
        repository: EmployeeRepository,
        email_service: EmailService,
    ):
        self.repository = repository
        self.email_service = email_service

    def create_employee(
        self,
        db,
        employee_data: Employee,
    ) -> EmployeeSchema:
        """
        Create an employee and email the generated credentials.

        The database session is accepted for compatibility with the
        router/service contract. The repository already owns the
        configured database session.
        """

        employee, username, temporary_password = (
            self.repository.create_new_employee(
                employee_data,
                return_credentials=True,
            )
        )

        self.email_service.send_initial_credentials(
            recipient_email=employee.email,
            username=username,
            temporary_password=temporary_password,
        )

        return employee


def get_employee_service(
    db,
) -> EmployeeService:
    """
    Create an employee service with the application's dependencies.
    """

    repository = EmployeeRepository(db)

    email_service = EmailService(
        api_key=settings.SENDGRID_API_KEY or "",
        from_email=settings.SENDGRID_FROM_EMAIL or "",
    )


    return EmployeeService(
        repository=repository,
        email_service=email_service,
    )
