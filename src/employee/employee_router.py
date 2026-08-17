from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_db
from employee.employee_model import Employee
from employee.employee_reponse import EmployeeResponse
from repositories.employee_repository import EmployeeRepository

router = APIRouter()

@router.post("/employees", response_model=EmployeeResponse, status_code=201)
async def post_new_employee(employee_data: Employee, db: Session = Depends(get_db)):
    """
    Create a new employee record and return the created employee.
    """
    repo = EmployeeRepository(db)

    try:
        new_employee = repo.create_new_employee(employee_data)
        return new_employee

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Employee with this email already exists."
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
