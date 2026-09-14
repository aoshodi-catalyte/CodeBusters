from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from exceptions.employee_exceptions import EmployeeNotFoundError
from repositories.employee_repository import EmployeeRepository


def get_acting_user(token_payload: dict, db: Session):
    employee_repo = EmployeeRepository(db)
    user_id = token_payload.get("employee_id")

    try:
        return employee_repo.get_employee_by_id(user_id)
    except EmployeeNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc
