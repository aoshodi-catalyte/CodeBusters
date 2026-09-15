import pytest
from pydantic import ValidationError

from password_reset.password_reset_model import (
    PasswordResetConfirmRequest,
)


def test_password_reset_accepts_valid_password():
    request = PasswordResetConfirmRequest(
        username="john.smith",
        code="482193",
        new_password="SecurePassword12",
    )

    assert request.username == "john.smith"
    assert request.code == "482193"
    assert request.new_password == "SecurePassword12"


def test_password_reset_rejects_password_shorter_than_12_characters():
    with pytest.raises(ValidationError):
        PasswordResetConfirmRequest(
            username="john.smith",
            code="482193",
            new_password="SecurePass1",
        )


def test_password_reset_rejects_password_without_uppercase():
    with pytest.raises(ValidationError):
        PasswordResetConfirmRequest(
            username="john.smith",
            code="482193",
            new_password="securepassword12",
        )


def test_password_reset_rejects_password_without_lowercase():
    with pytest.raises(ValidationError):
        PasswordResetConfirmRequest(
            username="john.smith",
            code="482193",
            new_password="SECUREPASSWORD12",
        )


def test_password_reset_rejects_password_without_number():
    with pytest.raises(ValidationError):
        PasswordResetConfirmRequest(
            username="john.smith",
            code="482193",
            new_password="SecurePassword",
        )


def test_password_reset_accepts_password_without_special_character():
    request = PasswordResetConfirmRequest(
        username="john.smith",
        code="482193",
        new_password="SecurePassword12",
    )

    assert request.new_password == "SecurePassword12"


def test_password_reset_rejects_password_over_72_characters():
    long_password = (
        "A"
        + ("a" * 70)
        + "1"
        + "X"
    )

    assert len(long_password) == 73

    with pytest.raises(ValidationError):
        PasswordResetConfirmRequest(
            username="john.smith",
            code="482193",
            new_password=long_password,
        )


def test_password_reset_accepts_exactly_72_characters():
    valid_password = (
        "A"
        + ("a" * 70)
        + "1"
    )

    assert len(valid_password) == 72

    request = PasswordResetConfirmRequest(
        username="john.smith",
        code="482193",
        new_password=valid_password,
    )

    assert request.new_password == valid_password
