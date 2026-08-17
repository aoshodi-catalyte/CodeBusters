from fastapi import FastAPI, Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
from database import Base, SessionLocal, engine, get_db
from vendor.vendor_model import VendorBase
from vendor.vendor_schema import VendorSchema
from repositories.vendor_repository import VendorRepository
from ingredient.ingredient_schema import IngredientSchema, AllergenSchema
from baked_good.baked_good_schema import BakedGoodSchema

router = APIRouter()

# def get_db():
#     """Provide a database session for request‑scoped dependency injection.

#     Creates a new SQLAlchemy session, yields it to the request handler, and
#     ensures the session is properly closed after the request completes.

#     Yields:
#         Session: An active SQLAlchemy session used for database operations.

#     Raises:
#         SQLAlchemyError: If the session fails to initialize or close properly.
#     """
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

@router.post("/vendor", response_model=VendorSchema, status_code=201)
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
    new_vendor = repo.create_new_vendor(vendor_data)
    return new_vendor

@router.get("/vendor", response_model=list[VendorSchema])
async def get_all_vendors(db: Session = Depends(get_db)):
    """Retrieve and return all vendors stored in the system.

    Queries the database for all vendor records and returns them as a list of
    response safe schema objects.

    Args:
        db (Session): Database session injected via FastAPI dependency.

    Returns:
        list[VendorSchema]: A list of all vendors currently stored in the database.
    """
    repo = VendorRepository(db)
    return repo.get_all_vendors()

@router.get("/vendor/{vendor_id}", response_model=VendorSchema)
async def get_vendor(vendor_id: int, db: Session = Depends(get_db)):
    """Retrieve a single vendor by its unique identifier.

    Looks up a vendor using its primary key. If the vendor does not exist,
    a 404 HTTPException is raised.

    Args:
        vendor_id (int): The unique identifier of the vendor to retrieve.
        db (Session): Database session injected via FastAPI dependency.

    Returns:
        VendorSchema: The vendor matching the provided ID.

    Raises:
        HTTPException: If no vendor exists with the given ID.
    """
    repo = VendorRepository(db)
    vendor = repo.get_vendor_by_id(vendor_id)
    if vendor is None:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return vendor