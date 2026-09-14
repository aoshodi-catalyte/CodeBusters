"""
Utility functions for extracting the acting user from a JWT payload.

This module centralizes authentication logic used across multiple routers
to ensure consistent handling of employee lookup and authorization.
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from exceptions.employee_exceptions import EmployeeNotFoundError
from repositories.employee_repository import EmployeeRepository


def get_acting_user(token_payload: dict, db: Session):
    """
    Retrieve the acting employee based on the JWT payload.

    This function extracts the `employee_id` from the token payload and
    queries the database to fetch the corresponding employee record.
    If the employee cannot be found, an HTTP 401 Unauthorized error is raised.

    Args:
        token_payload (dict):
            The decoded JWT payload containing the acting employee's ID.
        db (Session):
            Database session used to query employee records.

    Returns:
        EmployeeSchema:
            The employee associated with the ID found in the token payload.

    Raises:
        HTTPException:
            Raised with status 401 if the employee does not exist.
    """
    employee_repo = EmployeeRepository(db)
    user_id = token_payload.get("employee_id")

    try:
        return employee_repo.get_employee_by_id(user_id)
    except EmployeeNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc
