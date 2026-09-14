import pytest

from utils.password_utils import validate_password_strength


def test_valid_password_passes():
    password = "SecurePassword12"

    result = validate_password_strength(password)

    assert result == password


def test_password_with_11_characters_is_rejected():
    with pytest.raises(
        ValueError,
        match="12 characters",
    ):
        validate_password_strength("SecurePass1")


def test_password_without_uppercase_is_rejected():
    with pytest.raises(
        ValueError,
        match="uppercase",
    ):
        validate_password_strength("securepassword12")


def test_password_without_lowercase_is_rejected():
    with pytest.raises(
        ValueError,
        match="lowercase",
    ):
        validate_password_strength("SECUREPASSWORD12")


def test_password_without_number_is_rejected():
    with pytest.raises(
        ValueError,
        match="number",
    ):
        validate_password_strength("SecurePassword")


def test_special_character_is_not_required():
    password = "SecurePassword12"

    result = validate_password_strength(password)

    assert result == password
