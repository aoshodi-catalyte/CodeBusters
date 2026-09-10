"""
FastAPI router for vendor-related API endpoints, including creation of new
vendor records and handling of database integrity errors.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_audit_db, get_db
from employee.employee_schema import EmployeeSchema
from exceptions.vendor_exceptions import (
    DuplicateVendorException,
    VendorNotFoundException,
)
from repositories.vendor_repository import VendorAuditRepository, VendorRepository
from routers.secure_login_router import get_current_employee
from security.secure_manager_login import check_role
from vendor.vendor_model import VendorBase
from vendor.vendor_response import VendorResponse

router = APIRouter()


@router.post("/vendors", dependencies=[Depends(check_role(["manager"]))],
             response_model=VendorResponse, status_code=201)
async def post_new_vendor(
    vendor_data: VendorBase,
    db: Session = Depends(get_db),
):
    """Create a new vendor record and return the created vendor.

    Accepts validated vendor input data, delegates persistence to the
    VendorRepository, and returns the newly created vendor in API safe
    schema form.

    Args:
        vendor_data (VendorBase): Validated vendor attributes provided
            in the request body.
        db (Session): Database session injected via FastAPI dependency.

    Returns:
        VendorResponse: The newly created vendor.

    Raises:
        HTTPException: If a vendor with the same unique information
            already exists.
    """
    repo = VendorRepository(db)

    try:
        new_vendor = repo.create_new_vendor(vendor_data)
        return new_vendor

    except DuplicateVendorException as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.get(
    "/vendors",
    response_model=list[VendorResponse],
    status_code=status.HTTP_200_OK,
)
async def get_all_vendors(db: Session = Depends(get_db)):
    """Retrieve all vendor records.

    Args:
        db (Session): Database session injected via FastAPI dependency.

    Returns:
        list[VendorResponse]: A list of all vendors. Returns an empty list
            when no vendors exist.
    """
    repo = VendorRepository(db)

    return repo.get_all_vendors()


@router.get(
    "/vendors/{vendor_id}",
    response_model=VendorResponse,
    status_code=status.HTTP_200_OK,
)
def get_vendor_by_id(
    vendor_id: int,
    db: Session = Depends(get_db),
):
    """Retrieve a single vendor by ID.

    Args:
        vendor_id (int): The positive unique identifier of the vendor.
        db (Session): Database session injected through FastAPI dependency
            injection.

    Returns:
        VendorResponse: The requested vendor.

    Raises:
        HTTPException: If the vendor does not exist.
    """
    repo = VendorRepository(db)

    try:
        return repo.get_vendor_by_id(vendor_id)
    except VendorNotFoundException as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.put(
    "/vendors/{vendor_id}",
    dependencies=[Depends(check_role(["manager"]))],
    response_model=VendorResponse,
    status_code=status.HTTP_200_OK,
)
def update_vendor(
    vendor_id: int,
    vendor_data: VendorBase,
    db: Session = Depends(get_db),
):
    """Update an existing vendor.

    Args:
        vendor_id: The unique identifier of the vendor.
        vendor_data: Validated vendor properties.
        db: Database session injected through FastAPI dependency injection.

    Returns:
        VendorResponse: The updated vendor.

    Raises:
        HTTPException: If the vendor does not exist or a unique constraint
            is violated.
    """
    repo = VendorRepository(db)

    try:
        return repo.update_vendor(vendor_id, vendor_data)

    except VendorNotFoundException as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except DuplicateVendorException as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.delete(
    "/vendors/{vendor_id}",
    dependencies=[Depends(check_role(["manager"]))],
    status_code=status.HTTP_204_NO_CONTENT,
)
def deactivate_vendor(
    vendor_id: int,
    user: EmployeeSchema = Depends(get_current_employee),
    db: Session = Depends(get_db),
    audit_db: Session = Depends(get_audit_db)
):
    """Deactivate a vendor (soft delete) by setting active to False.

    The vendor's record is preserved for historical purposes.

    Args:
        vendor_id: The unique identifier of the vendor.
        db: Database session injected through FastAPI dependency
            injection.

    Raises:
        HTTPException: If the vendor does not exist.
    """
    repo = VendorRepository(db)
    audit_repo = VendorAuditRepository(audit_db)

    try:
        repo.deactivate_vendor(vendor_id, user.email, audit_repo)

    except VendorNotFoundException as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
