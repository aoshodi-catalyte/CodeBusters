"""
Provides FastAPI dependencies related to authentication, including
retrieving the acting user from a JWT token.
"""

from fastapi import Depends, HTTPException, status
from database import get_db
from repositories.employee_repository import EmployeeRepository
from exceptions.employee_exceptions import EmployeeNotFoundError
from utils.jwt_utils import get_token_from_header, decode_token


def get_acting_user(
    token: str = Depends(get_token_from_header),
    db=Depends(get_db)
):
    """
    Retrieve the acting employee based on the JWT provided in the
    Authorization header.

    The token is decoded to extract the `employee_id`, which is then
    used to look up the corresponding employee record. If the employee
    does not exist, a 401 Unauthorized error is raised.

    Args:
        token: The raw JWT extracted from the Authorization header.
        db: The SQLAlchemy session used to query employee data.

    Returns:
        EmployeeSchema: The employee represented by the JWT.

    Raises:
        HTTPException: If the employee referenced in the token does not exist.
    """
    payload = decode_token(token)
    user_id = payload["employee_id"]

    repo = EmployeeRepository(db)

    try:
        return repo.get_employee_by_id(user_id)
    except EmployeeNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc
