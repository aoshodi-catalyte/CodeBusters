"""
Repository logic for initiating and confirming employee password resets.
"""

from datetime import datetime, timedelta, timezone
import secrets

from sqlalchemy.orm import Session

from password_reset.password_reset_model import PasswordResetChannel
from password_reset.password_reset_schema import PasswordResetToken
from secure_login.secure_login_schema import EmployeeAuth
from utils.password_utils import hash_password, verify_password


class PasswordResetRepository:
    """
    Handles creation and confirmation of password reset requests.
    """

    RESET_CODE_EXPIRATION_MINUTES = 10

    def generate_reset_code(self) -> str:
        """
        Generate a secure six-digit password reset code.
        """

        return str(
            secrets.randbelow(900000) + 100000
        )

    @staticmethod
    def _ensure_utc(value: datetime) -> datetime:
        """
        Normalize a datetime to timezone-aware UTC.

        SQLite may return timezone-naive datetimes even when the
        SQLAlchemy column uses timezone=True.
        """

        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)

        return value.astimezone(timezone.utc)

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

    def confirm_reset(
        self,
        db: Session,
        username: str,
        code: str,
        new_password: str,
    ) -> None:
        """
        Verify a password reset code and set a new password.

        The reset code must:
            - belong to the employee
            - not already be used
            - not be expired
            - match the stored hash

        A successful reset:
            - replaces the employee password hash
            - clears the temporary-password flag
            - marks the reset token as used
        """

        auth = (
            db.query(EmployeeAuth)
            .filter(
                EmployeeAuth.username == username
            )
            .first()
        )

        if auth is None:
            raise ValueError(
                "Invalid or expired password reset request."
            )

        reset_record = (
            db.query(PasswordResetToken)
            .filter(
                PasswordResetToken.employee_id == auth.employee_id,
                PasswordResetToken.used_at.is_(None),
            )
            .order_by(
                PasswordResetToken.id.desc()
            )
            .first()
        )

        if reset_record is None:
            raise ValueError(
                "Invalid or expired password reset request."
            )

        now = datetime.now(timezone.utc)

        expires_at = self._ensure_utc(
            reset_record.expires_at
        )

        if expires_at <= now:
            raise ValueError(
                "Invalid or expired password reset request."
            )

        if not verify_password(
            code,
            reset_record.token_hash,
        ):
            raise ValueError(
                "Invalid or expired password reset request."
            )

        auth.password_hash = hash_password(
            new_password
        )

        auth.is_temporary_password = False

        reset_record.used_at = now

        db.commit()
        db.refresh(auth)
        db.refresh(reset_record)
