from fastapi import FastAPI, Depends, HTTPException, APIRouter, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from database import Base, get_db, engine
from employee.employee_model import Employee
from employee.employee_reponse import EmployeeResponse
from repositories.employee_repository import EmployeeRepository


router = APIRouter()

get_db()

@router.post("/employee", response_model=EmployeeResponse, status_code=201)
async def post_new_vendor(employee_data: Employee, db: Session = Depends(get_db)):
    """Create a new vendor record and return the created vendor.

    Accepts validated vendor input data, delegates persistence to the
    VendorRepository, and returns the newly created vendor in API safe schema form.

    Args:
        vendor_data (VendorBase): Validated vendor attributes provided in the request body.
        db (Session): Database session injected via FastAPI dependency.

    Returns:
        VendorSchema: The newly created vendor serialized into a response schema.

    Raises:
        HTTPException: If vendor creation fails due to database or validation issues.
    """
    repo = EmployeeRepository(db)
    try:
        new_employee = repo.create_new_vendor(employee_data)
        return new_employee
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Vendor with this contact name or email already exists."
        )