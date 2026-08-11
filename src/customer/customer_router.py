from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.database import get_db
from src.customer.customer_model import Customer
from src.customer.customer_schema import CustomerSchema


router = APIRouter()

@router.post("/customers", response_model=Customer)
def create_customer(
    customer: Customer,
    db: Session = Depends(get_db)
):
    """
    Creates a new customer and persists it to the database.
    """

    db_customer = CustomerSchema(
        first_name=customer.first_name,
        last_name=customer.last_name,
        email=customer.email,
        phone_number=customer.phone_number,
        active=customer.active,
        loyalty_points=customer.loyalty_points
    )

    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)

    return db_customer