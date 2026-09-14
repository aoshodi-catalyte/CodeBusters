import pytest
from pydantic import ValidationError

from config import Settings


def test_settings_require_jwt_secret(monkeypatch):
    monkeypatch.setenv(
        "DATABASE_URL",
        "sqlite:///:memory:",
    )

    monkeypatch.delenv(
        "JWT_SECRET_KEY",
        raising=False,
    )

    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_settings_load_jwt_secret(monkeypatch):
    monkeypatch.setenv(
        "DATABASE_URL",
        "sqlite:///:memory:",
    )

    monkeypatch.setenv(
        "JWT_SECRET_KEY",
        "test-secret-key",
    )

    settings = Settings(_env_file=None)

    assert settings.JWT_SECRET_KEY == "test-secret-key"
    assert settings.JWT_ALGORITHM == "HS256"
    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 30


def test_external_service_settings_are_optional(monkeypatch):
    monkeypatch.setenv(
        "DATABASE_URL",
        "sqlite:///:memory:",
    )

    monkeypatch.setenv(
        "JWT_SECRET_KEY",
        "test-secret-key",
    )

    monkeypatch.delenv(
        "SENDGRID_API_KEY",
        raising=False,
    )

    monkeypatch.delenv(
        "SENDGRID_FROM_EMAIL",
        raising=False,
    )

    monkeypatch.delenv(
        "TWILIO_ACCOUNT_SID",
        raising=False,
    )

    monkeypatch.delenv(
        "TWILIO_AUTH_TOKEN",
        raising=False,
    )

    monkeypatch.delenv(
        "TWILIO_FROM_PHONE",
        raising=False,
    )

    settings = Settings(_env_file=None)

    assert settings.SENDGRID_API_KEY is None
    assert settings.SENDGRID_FROM_EMAIL is None
    assert settings.TWILIO_ACCOUNT_SID is None
    assert settings.TWILIO_AUTH_TOKEN is None
    assert settings.TWILIO_VERIFY_SERVICE_SID is None