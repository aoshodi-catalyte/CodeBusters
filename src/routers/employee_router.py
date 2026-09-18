"""
FastAPI router for employee-related API endpoints, including creation and
retrieval of employee records and validation of repository-level errors.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_db
from employee.employee_model import Employee
from employee.employee_response import EmployeeResponse
from exceptions.employee_exceptions import (
    EmployeeEmailAlreadyExistsError,
    EmployeeAlreadyDeactivatedError,
)
from exceptions.secure_login_exceptions import EmployeeNotFoundError
from repositories.employee_repository import EmployeeRepository
from security.secure_manager_login import check_role
from services.employee_service import get_employee_service


router = APIRouter()


@router.post(
    "/employees",
    dependencies=[Depends(check_role(["manager"]))],
    response_model=EmployeeResponse,
    status_code=201,
)
async def post_new_employee(
    employee_data: Employee,
    db: Session = Depends(get_db),
):
    """
    Create a new employee record and email the generated credentials.

    The employee service coordinates:
        - employee creation
        - username generation
        - temporary password generation
        - initial credential email delivery
    """

    service = get_employee_service(db)

    try:
        new_employee = service.create_employee(
            db,
            employee_data,
        )

        return new_employee

    except IntegrityError as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Employee with this email already exists.",
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get(
    "/employees",
    response_model=list[EmployeeResponse],
    status_code=status.HTTP_200_OK,
)
async def get_all_employees(
    db: Session = Depends(get_db),
):
    """
    Retrieve all employee records.

    Args:
        db:
            SQLAlchemy database session.

    Returns:
        A list of all employees.
    """

    repo = EmployeeRepository(db)

    return repo.get_all_employees()


def _handle_repo_errors(exc: Exception) -> None:
    """
    Convert repository exceptions into HTTPExceptions.
    """

    if isinstance(exc, EmployeeNotFoundError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    if isinstance(exc, EmployeeEmailAlreadyExistsError):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    raise exc


@router.get(
    "/employees/{employee_id}",
    response_model=EmployeeResponse,
    status_code=status.HTTP_200_OK,
)
def get_single_employee_by_id(
    employee_id: int,
    db: Session = Depends(get_db),
):
    """
    Retrieve a single employee by ID.
    """

    repo = EmployeeRepository(db)

    try:
        return repo.get_employee_by_id(employee_id)

    except EmployeeNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.put(
    "/employees/{employee_id}",
    dependencies=[Depends(check_role(["manager"]))],
    response_model=EmployeeResponse,
    status_code=status.HTTP_200_OK,
)
def update_employee(
    employee_id: int,
    employee: Employee,
    db: Session = Depends(get_db),
):
    """
    Update an existing employee's properties.

    Raises:
        HTTPException 404:
            If no employee exists with the provided ID.

        HTTPException 409:
            If the updated email belongs to another employee.
    """

    repo = EmployeeRepository(db)

    try:
        return repo.update_employee(
            employee_id,
            employee,
        )

    except EmployeeNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except EmployeeEmailAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.delete(
    "/employees/{employee_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def deactivate_employee(
    employee_id: int,
    db: Session = Depends(get_db),
):
    """
    Deactivate an employee by setting active to False.

    The employee record is preserved for historical purposes.

    Raises:
        HTTPException 404:
            If the employee does not exist.

        HTTPException 409:
            If the employee is already deactivated.
    """

    repo = EmployeeRepository(db)

    try:
        repo.deactivate_employee(employee_id)

    except EmployeeNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except EmployeeAlreadyDeactivatedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
