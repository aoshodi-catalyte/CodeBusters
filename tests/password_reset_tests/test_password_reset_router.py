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


def test_password_reset_confirm_success(client):
    captured = {}

    class FakePasswordResetService:
        def confirm_reset(
            self,
            db,
            username,
            code,
            new_password,
        ):
            captured["db"] = db
            captured["username"] = username
            captured["code"] = code
            captured["new_password"] = new_password

    fake_service = FakePasswordResetService()

    client.app.dependency_overrides[
        password_reset_router.get_password_reset_service
    ] = lambda: fake_service

    try:
        response = client.post(
            "/password-reset/confirm",
            json={
                "username": "john.smith",
                "code": "482193",
                "new_password": "NewPassword123!",
            },
        )
    finally:
        client.app.dependency_overrides.pop(
            password_reset_router.get_password_reset_service,
            None,
        )

    assert response.status_code == 200

    assert response.json() == {
        "message": "Password reset successfully"
    }

    assert captured["username"] == "john.smith"
    assert captured["code"] == "482193"
    assert captured["new_password"] == "NewPassword123!"


def test_password_reset_confirm_invalid_or_expired_code(client):
    class FakePasswordResetService:
        def confirm_reset(
            self,
            db,
            username,
            code,
            new_password,
        ):
            raise ValueError(
                "Password reset code is invalid or expired."
            )

    fake_service = FakePasswordResetService()

    client.app.dependency_overrides[
        password_reset_router.get_password_reset_service
    ] = lambda: fake_service

    try:
        response = client.post(
            "/password-reset/confirm",
            json={
                "username": "john.smith",
                "code": "482193",
                "new_password": "NewPassword123!",
            },
        )
    finally:
        client.app.dependency_overrides.pop(
            password_reset_router.get_password_reset_service,
            None,
        )

    assert response.status_code == 400

    assert response.json() == {
        "detail": "Invalid or expired password reset request."
    }


def test_password_reset_confirm_invalid_code_length(client):
    response = client.post(
        "/password-reset/confirm",
        json={
            "username": "john.smith",
            "code": "123",
            "new_password": "NewPassword123!",
        },
    )

    assert response.status_code == 422


def test_password_reset_confirm_new_password_too_short(client):
    response = client.post(
        "/password-reset/confirm",
        json={
            "username": "john.smith",
            "code": "482193",
            "new_password": "short",
        },
    )

    assert response.status_code == 422


def test_password_reset_confirm_missing_username(client):
    response = client.post(
        "/password-reset/confirm",
        json={
            "code": "482193",
            "new_password": "NewPassword123!",
        },
    )

    assert response.status_code == 422


def test_password_reset_confirm_missing_code(client):
    response = client.post(
        "/password-reset/confirm",
        json={
            "username": "john.smith",
            "new_password": "NewPassword123!",
        },
    )

    assert response.status_code == 422


def test_password_reset_confirm_missing_new_password(client):
    response = client.post(
        "/password-reset/confirm",
        json={
            "username": "john.smith",
            "code": "482193",
        },
    )

    assert response.status_code == 422
