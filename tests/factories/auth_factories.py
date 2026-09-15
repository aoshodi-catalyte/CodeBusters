"""
Factory utilities for generating authentication tokens used in tests.

This module provides helper functions for creating JWTs that simulate
authenticated users with specific roles, allowing tests to exercise
authorization logic without relying on the real login flow.
"""

from datetime import datetime, UTC, timedelta
from uuid import uuid4

from jose import jwt

from config import settings


def _base_payload(employee_id: int, role: str):
    now = datetime.now(UTC)
    return {
        "sub": str(employee_id),
        "employee_id": employee_id,
        "role": role,
        "jti": str(uuid4()),              # REQUIRED
        "iat": now,
        "exp": now + timedelta(hours=1),  # REQUIRED
    }


def manager_token():
    """
    Generate a JWT token representing a manager‑level employee.

    Returns
    -------
    str
        A signed JWT containing the employee ID and manager role,
        suitable for use in Authorization headers during tests.
    """
    payload = _base_payload(employee_id=1, role="manager")
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def employee_token():
    """
    Generate a JWT token representing a standard employee.

    Used to verify that employee-level users are restricted from
    manager-only routes but allowed on employee-accessible routes.
    """
    payload = _base_payload(employee_id=2, role="employee")
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
