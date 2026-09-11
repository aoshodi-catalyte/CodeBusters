"""
Application service for password reset initiation.
"""

from password_reset.password_reset_model import PasswordResetChannel
from repositories.password_reset_repository import PasswordResetRepository
from services.email_service import EmailService
from services.sms_service import SmsService


class PasswordResetService:
    """
    Coordinates password reset creation and delivery.
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
            self.sms_service.send_password_reset_code(
                employee.phone_number,
                code,
            )
