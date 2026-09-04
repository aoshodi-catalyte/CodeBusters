"""
FastAPI router for employee-related API endpoints, including creation and
retrieval of employee records and validation of repository-level errors.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_db
from employee.employee_model import Employee
from employee.employee_reponse import EmployeeResponse
from exceptions.secure_login_exceptions import EmployeeNotFoundError
from repositories.employee_repository import EmployeeRepository

router = APIRouter()


@router.post("/employees", response_model=EmployeeResponse, status_code=201)
async def post_new_employee(employee_data: Employee, db: Session = Depends(get_db)):
    """
    Create a new employee record and return the newly created employee.

    This endpoint accepts validated employee input data, delegates creation
    logic to the EmployeeRepository, and returns the resulting persisted
    employee record. It also handles common error scenarios such as duplicate
    emails and invalid business rules.

    Args:
        employee_data (Employee):
            Pydantic model containing the employee fields submitted by the client.
            Includes validation for email format, role normalization, date parsing,
            and business rules.
        db (Session):
            SQLAlchemy database session provided via FastAPI dependency injection.

    Returns:
        EmployeeResponse:
            A serialized representation of the newly created employee, including
            its assigned database ID and normalized role.

    Raises:
        HTTPException (409 Conflict):
            Raised when an IntegrityError occurs, typically due to attempting to
            create an employee with an email that already exists in the database.
        HTTPException (400 Bad Request):
            Raised when the repository encounters a ValueError, usually triggered
            by invalid role mappings or business rule violations.
    """

    repo = EmployeeRepository(db)

    try:
        new_employee = repo.create_new_employee(employee_data)
        return new_employee

    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Employee with this email already exists.",
        ) from exc

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e


@router.get(
    "/employees",
    response_model=list[EmployeeResponse],
    status_code=status.HTTP_200_OK,
)
async def get_all_employees(db: Session = Depends(get_db)):
    """
    Retrieve all employee records.

    Args:
        db (Session):
            SQLAlchemy database session provided via FastAPI dependency injection.

    Returns:
        list[EmployeeResponse]:
            A list of all employees. Returns an empty list when no employees
            exist.
    """

    repo = EmployeeRepository(db)
    return repo.get_all_employees()


@router.get(
    "/employees/{employee_id}",
    response_model=EmployeeResponse,
    status_code=status.HTTP_200_OK,
)
def get_single_employee_by_id(
    employee_id: int,
    db: Session = Depends(get_db),
):
    """Retrieve a single employee by ID.

    Args:
        employee_id (int): The positive unique identifier of the employee.
        db (Session): Database session injected through FastAPI dependency
            injection.

    Returns:
        EmployeeResponse: The requested employee.

    Raises:
        HTTPException: If the employee does not exist.
    """
    repo = EmployeeRepository(db)

    try:
        return repo.get_employee_by_id(employee_id)
    except EmployeeNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
