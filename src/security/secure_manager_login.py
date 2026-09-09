"""
Security utilities for role‑based authorization in the FastAPI application.

This module defines the `check_role` dependency, which validates the user's
JWT token, extracts the assigned role, and ensures the user has permission
to access protected routes. Unauthorized or invalid access attempts are
logged and rejected with appropriate HTTP error responses.
"""

import logging
from datetime import datetime, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt  # type: ignore

from config import settings

SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def check_role(allowed_roles: list[str]):
    """
    Creates a FastAPI dependency that enforces role‑based access control.

    Parameters
    ----------
    allowed_roles : list[str]
        A list of roles permitted to access the protected route.

    Returns
    -------
    Callable
        A dependency function that validates the JWT token, checks the user's
        role, and either returns the decoded payload or raises an HTTPException
        if access is unauthorized.
    """
    def role_checker(token: str = Depends(oauth2_scheme)):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_role = payload.get("role")

            if user_role not in allowed_roles:
                logger.warning(
                    "Unauthorized access attempt at %s Role '%s' tried to access manager-only route.",
                    datetime.now(timezone.utc),
                    user_role,
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have permission to perform this action."
                )

            return payload

        except JWTError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token."
            ) from exc

    return role_checker
