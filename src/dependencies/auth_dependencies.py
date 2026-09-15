"""
Authentication dependencies for FastAPI routes.

This module provides reusable dependencies for retrieving the authenticated
employee's identity from a JWT access token and accessing the database.
"""

# dependencies/auth_dependencies.py

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from database import get_db
from repositories.secure_login_repository import SecureLoginRepository


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

auth_repo = SecureLoginRepository()


def get_current_employee_id(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> int:
    """
    Retrieve the authenticated employee ID from the JWT token.

    Args:
        token (str): JWT access token from the Authorization header.
        db (Session): Active database session.

    Returns:
        int: ID of the authenticated employee.
    """
    employee = auth_repo.get_current_employee(token, db)
    return employee.id
