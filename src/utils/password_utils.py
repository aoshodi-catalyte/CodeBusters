"""
Password hashing and verification utilities.
"""

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
