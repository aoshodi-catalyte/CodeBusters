"""
FastAPI endpoints for password reset initiation.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from config import settings
from database import get_db
from password_reset.password_reset_model import (
    PasswordResetInitiateRequest,
)
from repositories.password_reset_repository import (
    PasswordResetRepository,
)
from services.email_service import EmailService
from services.password_reset_service import PasswordResetService
from services.sms_service import SmsService


router = APIRouter(
    prefix="/password-reset",
    tags=["password-reset"],
)


def get_password_reset_service() -> PasswordResetService:
    email_service = EmailService(
        api_key=settings.SENDGRID_API_KEY or "",
        from_email=settings.SENDGRID_FROM_EMAIL or "",
    )

    sms_service = SmsService(
        account_sid=settings.TWILIO_ACCOUNT_SID or "",
        auth_token=settings.TWILIO_AUTH_TOKEN or "",
        from_phone=settings.TWILIO_FROM_PHONE or "",
    )

    return PasswordResetService(
        repository=PasswordResetRepository(),
        email_service=email_service,
        sms_service=sms_service,
    )


@router.post("/initiate")
def initiate_password_reset(
    data: PasswordResetInitiateRequest,
    db: Session = Depends(get_db),
    service: PasswordResetService = Depends(
        get_password_reset_service
    ),
):
    service.initiate_reset(
        db,
        data.username,
        data.channel,
    )

    return {
        "message": (
            "If the account exists and the selected "
            "verification method is available, "
            "a verification code has been sent."
        )
    }
