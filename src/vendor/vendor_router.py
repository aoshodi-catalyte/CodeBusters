from fastapi import FastAPI, Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
from src.database import Base, SessionLocal, engine
from src.vendor.vendor_model import VendorBase
from src.vendor.vendor_schema import VendorSchema
from src.repositories.vendor_repository import VendorRepository
from src.ingredient.ingredient_schema import IngredientSchema, AllergenSchema

router = APIRouter()
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/vendor", response_model=VendorSchema, status_code=201)
async def post_new_vendor(vendor_data: VendorBase, db: Session = Depends(get_db)):
    repo = VendorRepository(db)
    new_vendor = repo.create_new_vendor(vendor_data)
    return new_vendor

@router.get("/vendor", response_model=list[VendorSchema])
async def get_all_vendors(db: Session = Depends(get_db)):
    repo = VendorRepository(db)
    return repo.get_all_vendors()

@router.get("/vendor/{vendor_id}", response_model=VendorSchema)
async def get_vendor(vendor_id: int, db: Session = Depends(get_db)):
    repo = VendorRepository(db)
    vendor = repo.get_vendor_by_id(vendor_id)
    if vendor is None:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return vendor