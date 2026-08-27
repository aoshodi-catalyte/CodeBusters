"""
FastAPI router for vendor-related API endpoints, including creation of new
vendor records and handling of vendor domain exceptions.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from exceptions.vendor_exceptions import (
DuplicateVendorException,
VendorNotFoundException,
)
from repositories.vendor_repository import VendorRepository
from vendor.vendor_model import VendorBase
from vendor.vendor_response import VendorResponse

router = APIRouter()


@router.post("/vendors", response_model=VendorResponse, status_code=201)
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
