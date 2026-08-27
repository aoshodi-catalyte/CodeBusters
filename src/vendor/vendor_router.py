"""
FastAPI router for vendor-related API endpoints, including creation of new
vendor records and handling of database integrity errors.
"""

from fastapi import Depends, HTTPException, APIRouter, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from database import get_db
from vendor.vendor_model import VendorBase
from vendor.vendor_response import VendorResponse
from repositories.vendor_repository import VendorRepository

router = APIRouter()


@router.post("/vendors", response_model=VendorResponse, status_code=201)
async def post_new_vendor(vendor_data: VendorBase, db: Session = Depends(get_db)):
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
    repo = VendorRepository(db)
    try:
        new_vendor = repo.create_new_vendor(vendor_data)
        return new_vendor
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Vendor with this name or email already exists.",
        ) from exc

@router.get("/vendors", response_model=list[VendorResponse], status_code=status.HTTP_200_OK)
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
