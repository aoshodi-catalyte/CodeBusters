"""
Pydantic models used by the employee authentication endpoints.

These schemas validate credential creation and password changes before
the requests reach the repository layer.
"""

from pydantic import BaseModel, Field, field_validator

from utils.password_utils import validate_password_strength


class EmployeeAuthCreate(BaseModel):
    """
    Schema for creating employee authentication credentials.

    Attributes:
        employee_id (int):
            The ID of the employee receiving login credentials.
        username (str):
            The desired username for authentication.
        password (str):
            The password used when creating credentials.
    """

    employee_id: int
    username: str

    password: str = Field(
        min_length=12,
        max_length=72,
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        """
        Validate the password against the application's password policy.
        """

        return validate_password_strength(value)


class PasswordChangeRequest(BaseModel):
    """
    Request model for changing an employee password.

    The employee is identified by the authenticated JWT token.
    """

    current_password: str = Field(
        min_length=1,
        max_length=72,
    )

    new_password: str = Field(
        min_length=12,
        max_length=72,
    )

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, value: str) -> str:
        """
        Validate the new password against the application's password policy.
        """

        return validate_password_strength(value)
