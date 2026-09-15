"""
Password hashing and verification utilities.
"""
import re
from passlib.context import CryptContext


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    """

    return pwd_context.hash(password)


def verify_password(
    password: str,
    password_hash: str,
) -> bool:
    """
    Verify a password against its stored hash.
    """

    return pwd_context.verify(
        password,
        password_hash,
    )

def validate_password_strength(password: str) -> str:
    """
    Validate password strength requirements.

    Requirements:
        - At least 12 characters.
        - At least one uppercase letter.
        - At least one lowercase letter.
        - At least one number.
    """

    if len(password) < 12:
        raise ValueError(
            "Password must be at least 12 characters long."
        )

    if not re.search(r"[A-Z]", password):
        raise ValueError(
            "Password must contain at least one uppercase letter."
        )

    if not re.search(r"[a-z]", password):
        raise ValueError(
            "Password must contain at least one lowercase letter."
        )

    if not re.search(r"\d", password):
        raise ValueError(
            "Password must contain at least one number."
        )

    return password
