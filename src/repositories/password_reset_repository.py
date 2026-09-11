"""
Repository logic for initiating employee password resets.
"""

from datetime import datetime, timedelta, timezone
import secrets

from sqlalchemy.orm import Session

from password_reset.password_reset_model import PasswordResetChannel
from password_reset.password_reset_schema import PasswordResetToken
from secure_login.secure_login_schema import EmployeeAuth
from utils.password_utils import hash_password


class PasswordResetRepository:
    """
    Handles creation of password reset requests.
    """

    RESET_CODE_EXPIRATION_MINUTES = 10

    def generate_reset_code(self) -> str:
        """
        Generate a secure six-digit password reset code.
        """

        return str(
            secrets.randbelow(900000) + 100000
        )

    def initiate_reset(
        self,
        db: Session,
        username: str,
        channel: PasswordResetChannel,
    ):
        """
        Create a password reset request.

        Returns:
            A tuple containing the employee and plaintext reset code.

        The plaintext reset code is never stored in the database.
        Only its hash is persisted.
        """

        auth = (
            db.query(EmployeeAuth)
            .filter(
                EmployeeAuth.username == username
            )
            .first()
        )

        if auth is None:
            return None, None

        employee = auth.employee

        if channel == PasswordResetChannel.EMAIL:
            if not employee.email:
                return None, None

        elif channel == PasswordResetChannel.PHONE:
            if not employee.phone_number:
                return None, None

        code = self.generate_reset_code()

        reset_record = PasswordResetToken(
            employee_id=employee.id,
            token_hash=hash_password(code),
            expires_at=(
                datetime.now(timezone.utc)
                + timedelta(
                    minutes=self.RESET_CODE_EXPIRATION_MINUTES
                )
            ),
            channel=channel.value,
        )

        db.add(reset_record)
        db.commit()
        db.refresh(reset_record)

        return employee, code
