from types import SimpleNamespace

from password_reset.password_reset_model import PasswordResetChannel
from services.password_reset_service import PasswordResetService


def test_password_reset_sends_code_by_email():
    employee = SimpleNamespace(
        email="john@example.com",
        phone_number="5551234567",
    )

    repository = SimpleNamespace()
    email_service = SimpleNamespace()
    sms_service = SimpleNamespace()

    captured = {}

    def initiate_reset(db, username, channel):
        captured["db"] = db
        captured["username"] = username
        captured["channel"] = channel

        return employee, "482193"

    def send_email(recipient_email, code):
        captured["email"] = recipient_email
        captured["email_code"] = code

    def send_sms(recipient_phone, code):
        captured["phone"] = recipient_phone
        captured["phone_code"] = code

    repository.initiate_reset = initiate_reset
    email_service.send_password_reset_code = send_email
    sms_service.send_password_reset_code = send_sms

    service = PasswordResetService(
        repository=repository,
        email_service=email_service,
        sms_service=sms_service,
    )

    fake_db = object()

    service.initiate_reset(
        db=fake_db,
        username="john.smith",
        channel=PasswordResetChannel.EMAIL,
    )

    assert captured["db"] is fake_db
    assert captured["username"] == "john.smith"
    assert captured["channel"] == PasswordResetChannel.EMAIL

    assert captured["email"] == "john@example.com"
    assert captured["email_code"] == "482193"

    assert "phone" not in captured
    assert "phone_code" not in captured


def test_password_reset_sends_code_by_phone():
    employee = SimpleNamespace(
        email="john@example.com",
        phone_number="5551234567",
    )

    repository = SimpleNamespace()
    email_service = SimpleNamespace()
    sms_service = SimpleNamespace()

    captured = {}

    def initiate_reset(db, username, channel):
        captured["db"] = db
        captured["username"] = username
        captured["channel"] = channel

        return employee, "583214"

    def send_email(recipient_email, code):
        captured["email"] = recipient_email
        captured["email_code"] = code

    def send_sms(recipient_phone, code):
        captured["phone"] = recipient_phone
        captured["phone_code"] = code

    repository.initiate_reset = initiate_reset
    email_service.send_password_reset_code = send_email
    sms_service.send_password_reset_code = send_sms

    service = PasswordResetService(
        repository=repository,
        email_service=email_service,
        sms_service=sms_service,
    )

    fake_db = object()

    service.initiate_reset(
        db=fake_db,
        username="john.smith",
        channel=PasswordResetChannel.PHONE,
    )

    assert captured["db"] is fake_db
    assert captured["username"] == "john.smith"
    assert captured["channel"] == PasswordResetChannel.PHONE

    assert captured["phone"] == "5551234567"
    assert captured["phone_code"] == "583214"

    assert "email" not in captured
    assert "email_code" not in captured


def test_password_reset_unknown_user_does_not_send_code():
    repository = SimpleNamespace()
    email_service = SimpleNamespace()
    sms_service = SimpleNamespace()

    captured = {
        "email_called": False,
        "sms_called": False,
    }

    def initiate_reset(db, username, channel):
        return None, None

    def send_email(recipient_email, code):
        captured["email_called"] = True

    def send_sms(recipient_phone, code):
        captured["sms_called"] = True

    repository.initiate_reset = initiate_reset
    email_service.send_password_reset_code = send_email
    sms_service.send_password_reset_code = send_sms

    service = PasswordResetService(
        repository=repository,
        email_service=email_service,
        sms_service=sms_service,
    )

    service.initiate_reset(
        db=object(),
        username="does.not.exist",
        channel=PasswordResetChannel.EMAIL,
    )

    assert captured["email_called"] is False
    assert captured["sms_called"] is False
    