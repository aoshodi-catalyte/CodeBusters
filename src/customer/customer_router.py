from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.database import create_db, get_db
from src.customer.customer_model import Customer
from src.customer.customer_schema import CustomerSchema


router = APIRouter()


@router.post(
    "/customers",
    response_model=Customer,
    status_code=status.HTTP_201_CREATED
)
def create_customer(
    customer: Customer,
    db: Session = Depends(get_db)
):
    """
    Creates a new customer and persists it to the database.

    Returns:
        The newly created customer.

    Raises:
        HTTPException 409:
            Email or phone number already exists.
        HTTPException 500:
            Unexpected database error.
    """

    db_customer = CustomerSchema(
        first_name=customer.first_name,
        last_name=customer.last_name,
        email=customer.email,
        phone_number=customer.phone_number,
        active=customer.active,
        loyalty_points=customer.loyalty_points
    )

    try:
        db.add(db_customer)
        db.commit()
        db.refresh(db_customer)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A customer with this email or phone number already exists."
        )

    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while creating the customer."
        )

    return db_customer


@router.get(
    "/customers",
    response_model=list[Customer],
    status_code=status.HTTP_200_OK
)
def get_customers(
    db: Session = Depends(get_db)
):
    """
    Retrieves all customers from the database.

    Returns:
        A list of all customers.

    Raises:
        HTTPException 404:
            No customers were found.
        HTTPException 500:
            Unexpected database error.
    """

    try:
        customers = db.query(CustomerSchema).all()

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving customers."
        )

    if not customers:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No customers found."
        )

    return customers