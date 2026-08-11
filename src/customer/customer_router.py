from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Generator, Optional
from sqlalchemy.orm import Session
from src.customer.customer_schema import CustomerSchema
from database import get_db, Base, engine, SessionLocal

router = APIRouter()

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/customers", response_model=List[CustomerSchema])
def get_customers(db: Session = Depends(get_db)):
    return db.query(CustomerSchema).all()

@router.post("/customers", response_model=CustomerSchema)
def create_customer(customer: CustomerSchema, db: Session = Depends(get_db)):
    return customer