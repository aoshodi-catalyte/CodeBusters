"""
Pydantic models for password reset requests.
"""

from enum import Enum

from pydantic import BaseModel, Field


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
    code: str = Field(min_length=6, max_length=6)
    new_password: str = Field(min_length=8, max_length=72)
