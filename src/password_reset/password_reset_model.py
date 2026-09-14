"""
Pydantic models for password reset requests.
"""

from enum import Enum

from pydantic import BaseModel, Field, field_validator

from utils.password_utils import validate_password_strength


class PasswordResetChannel(str, Enum):
    """
    Supported password reset delivery channels.
    """

    EMAIL = "email"
    PHONE = "phone"


class PasswordResetInitiateRequest(BaseModel):
    """
    Request data used to initiate a password reset.
    """

    username: str
    channel: PasswordResetChannel


class PasswordResetConfirmRequest(BaseModel):
    """
    Request used to verify a password reset code and set a new password.
    """

    username: str

    code: str = Field(
        min_length=6,
        max_length=6,
    )

    new_password: str = Field(
        min_length=12,
        max_length=72,
    )

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, value: str) -> str:
        """
        Validate the new password against the application's
        password-strength requirements.
        """

        return validate_password_strength(value)
