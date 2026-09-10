"""
Pydantic models for password reset requests.
"""

from enum import Enum

from pydantic import BaseModel


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
