"""
Application service for password reset initiation and confirmation.
"""

from datetime import datetime, timezone

from password_reset.password_reset_model import PasswordResetChannel
from password_reset.password_reset_schema import PasswordResetToken
from repositories.password_reset_repository import (
    PasswordResetRepository,
)
from secure_login.secure_login_schema import EmployeeAuth
from services.email_service import EmailService
from services.sms_service import SmsService
from utils.password_utils import hash_password


class PasswordResetService:
    """
    Coordinates password reset creation, delivery, and confirmation.
    """

    def __init__(
        self,
        repository: PasswordResetRepository,
        email_service: EmailService,
        sms_service: SmsService,
    ):
        self.repository = repository
        self.email_service = email_service
        self.sms_service = sms_service

    def initiate_reset(
        self,
        db,
        username: str,
        channel: PasswordResetChannel,
    ) -> None:
        """
        Create and deliver a password reset code.
        """

        employee, code = self.repository.initiate_reset(
            db,
            username,
            channel,
        )

        if employee is None or code is None:
            return

        if channel == PasswordResetChannel.EMAIL:
            self.email_service.send_password_reset_code(
                employee.email,
                code,
            )

        elif channel == PasswordResetChannel.PHONE:
            self.sms_service.send_verification(
                employee.phone_number,
            )

    def confirm_reset(
        self,
        db,
        username: str,
        code: str,
        new_password: str,
    ) -> None:
        """
        Verify a password reset request and set a new password.

        Email resets are verified using the stored password-reset code.

        Phone resets are verified using Twilio Verify. The reset channel
        is determined from the active password-reset record.
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

        channel = PasswordResetChannel(
            reset_record.channel
        )

        if channel == PasswordResetChannel.PHONE:
            employee = auth.employee

            verified = self.sms_service.check_verification(
                employee.phone_number,
                code,
            )

            if not verified:
                raise ValueError(
                    "Invalid or expired password reset request."
                )

            auth.password_hash = hash_password(
                new_password
            )

            auth.is_temporary_password = False

            reset_record.used_at = datetime.now(
                timezone.utc
            )

            db.commit()
            db.refresh(auth)
            db.refresh(reset_record)

            return

        self.repository.confirm_reset(
            db,
            username,
            code,
            new_password,
        )
