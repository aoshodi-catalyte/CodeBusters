"""
Shared helpers for authentication and password-reset operations.
"""

from datetime import datetime

from sqlalchemy.orm import Session

from password_reset.password_reset_schema import PasswordResetToken
from secure_login.secure_login_schema import EmployeeAuth
from utils.password_utils import hash_password


INVALID_RESET_MESSAGE = (
    "Invalid or expired password reset request."
)


def get_auth_by_username(
    db: Session,
    username: str,
):
    """Return authentication data for a username."""
    return (
        db.query(EmployeeAuth)
        .filter(
            EmployeeAuth.username == username
        )
        .first()
    )


def get_active_reset_record(
    db: Session,
    employee_id: int,
):
    """Return the most recent unused reset record."""
    return (
        db.query(PasswordResetToken)
        .filter(
            PasswordResetToken.employee_id == employee_id,
            PasswordResetToken.used_at.is_(None),
        )
        .order_by(
            PasswordResetToken.id.desc()
        )
        .first()
    )


def get_reset_context(
    db: Session,
    username: str,
):
    """
    Return the employee authentication record and active reset record.

    Raises:
        ValueError: When the username or reset request is invalid.
    """

    auth = get_auth_by_username(
        db,
        username,
    )

    if auth is None:
        raise ValueError(INVALID_RESET_MESSAGE)

    reset_record = get_active_reset_record(
        db,
        auth.employee_id,
    )

    if reset_record is None:
        raise ValueError(INVALID_RESET_MESSAGE)

    return auth, reset_record


def apply_password_reset(
    auth: EmployeeAuth,
    reset_record: PasswordResetToken,
    new_password: str,
    used_at: datetime,
) -> None:
    """Apply a new password and complete the reset request."""

    auth.password_hash = hash_password(
        new_password
    )

    auth.is_temporary_password = False
    reset_record.used_at = used_at
