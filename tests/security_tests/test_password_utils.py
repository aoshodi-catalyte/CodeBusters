from utils.password_utils import (
    hash_password,
    verify_password,
)


def test_hashed_password_can_be_verified():
    password = "SecurePassword12"

    password_hash = hash_password(password)

    assert password_hash != password
    assert verify_password(password, password_hash) is True


def test_wrong_password_is_rejected():
    password = "SecurePassword12"

    password_hash = hash_password(password)

    assert verify_password(
        "WrongPassword12",
        password_hash,
    ) is False
