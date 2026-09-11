from password_reset.password_reset_model import PasswordResetChannel
from routers import password_reset_router


def test_password_reset_initiate_email_success(client):
    captured = {}

    class FakePasswordResetService:
        def initiate_reset(
            self,
            db,
            username,
            channel,
        ):
            captured["db"] = db
            captured["username"] = username
            captured["channel"] = channel

    fake_service = FakePasswordResetService()

    client.app.dependency_overrides[
        password_reset_router.get_password_reset_service
    ] = lambda: fake_service

    try:
        response = client.post(
            "/password-reset/initiate",
            json={
                "username": "john.smith",
                "channel": "email",
            },
        )
    finally:
        client.app.dependency_overrides.pop(
            password_reset_router.get_password_reset_service,
            None,
        )

    assert response.status_code == 200

    assert response.json() == {
        "message": (
            "If the account exists and the selected "
            "verification method is available, "
            "a verification code has been sent."
        )
    }

    assert captured["username"] == "john.smith"
    assert captured["channel"] == PasswordResetChannel.EMAIL


def test_password_reset_initiate_phone_success(client):
    captured = {}

    class FakePasswordResetService:
        def initiate_reset(
            self,
            db,
            username,
            channel,
        ):
            captured["db"] = db
            captured["username"] = username
            captured["channel"] = channel

    fake_service = FakePasswordResetService()

    client.app.dependency_overrides[
        password_reset_router.get_password_reset_service
    ] = lambda: fake_service

    try:
        response = client.post(
            "/password-reset/initiate",
            json={
                "username": "john.smith",
                "channel": "phone",
            },
        )
    finally:
        client.app.dependency_overrides.pop(
            password_reset_router.get_password_reset_service,
            None,
        )

    assert response.status_code == 200

    assert response.json() == {
        "message": (
            "If the account exists and the selected "
            "verification method is available, "
            "a verification code has been sent."
        )
    }

    assert captured["username"] == "john.smith"
    assert captured["channel"] == PasswordResetChannel.PHONE


def test_password_reset_initiate_invalid_channel(client):
    response = client.post(
        "/password-reset/initiate",
        json={
            "username": "john.smith",
            "channel": "carrier_pigeon",
        },
    )

    assert response.status_code == 422


def test_password_reset_initiate_missing_username(client):
    response = client.post(
        "/password-reset/initiate",
        json={
            "channel": "email",
        },
    )

    assert response.status_code == 422
