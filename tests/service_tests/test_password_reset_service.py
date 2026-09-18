from types import SimpleNamespace

from password_reset.password_reset_model import PasswordResetChannel
from services.password_reset_service import PasswordResetService


def test_initiate_reset_sends_code_by_email(monkeypatch):
    employee = SimpleNamespace(
        id=7,
        email="employee@example.com",
        phone_number="+13125551234",
    )

    class FakeRepository:
        def initiate_reset(
            self,
            db,
            username,
            channel,
        ):
            assert username == "jane"
            assert channel == PasswordResetChannel.EMAIL

            return employee, "482193"

    captured = {}

    class FakeEmailService:
        def send_password_reset_code(
            self,
            recipient_email,
            code,
        ):
            captured["recipient_email"] = recipient_email
            captured["code"] = code

    class FakeSmsService:
        def send_password_reset_code(
            self,
            recipient_phone,
            code,
        ):
            raise AssertionError(
                "SMS service should not be called for email reset"
            )

    service = PasswordResetService(
        repository=FakeRepository(),
        email_service=FakeEmailService(),
        sms_service=FakeSmsService(),
    )

    service.initiate_reset(
        db=object(),
        username="jane",
        channel=PasswordResetChannel.EMAIL,
    )

    assert captured["recipient_email"] == "employee@example.com"
    assert captured["code"] == "482193"
