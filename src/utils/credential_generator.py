"""
Utilities for generating secure employee login credentials.
"""

import secrets
import string


def generate_temporary_password(length: int = 16) -> str:
    """
    Generate a secure random temporary password.

    Args:
        length: Number of characters in the password.

    Returns:
        A randomly generated temporary password.
    """
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"

    return "".join(
        secrets.choice(alphabet)
        for _ in range(length)
    )


def generate_username(first_name: str, last_name: str) -> str:
    """
    Generate a username based on the employee's name.

    The base username is created from the employee's first and last name.

    Example:
        John Smith -> john.smith

    Args:
        first_name: Employee first name.
        last_name: Employee last name.

    Returns:
        A normalized username candidate.
    """
    first = first_name.strip().lower()
    last = last_name.strip().lower()

    return f"{first}.{last}"
