"""
API routes for Customer operations.

This module handles HTTP requests and responses for customers.
Database operations are delegated to the customer repository.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import engine, get_db
from customer.customer_model import CustomerCreate, CustomerResponse
from customer.customer_repository import CustomerRepository
from customer.customer_schema import CustomerSchema


router = APIRouter()


# DEVELOPMENT ONLY:
# Reset the customer table whenever the application reloads.
def reset_customer_table() -> None:
    """
    Drop and recreate the customer table.

    This is intended for development only and will delete
    all existing customer records.
    """
    CustomerSchema.__table__.drop(
        bind=engine,
        checkfirst=True
    )

    CustomerSchema.__table__.create(
        bind=engine,
        checkfirst=True
    )


reset_customer_table()


@router.post(
    "/customers",
    response_model=CustomerResponse,
    status_code=status.HTTP_201_CREATED
)
def create_customer(
    customer: CustomerCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new customer and persist it to the database.

    The incoming phone number is validated and normalized by the
    CustomerCreate Pydantic model before being passed to the repository.
    The CustomerResponse model formats the phone number for the API response.

    Args:
        customer: Customer data provided by the API client.
        db: SQLAlchemy database session.

    Returns:
        CustomerResponse: The newly created customer.

    Raises:
        HTTPException 409:
            If the email or phone number already exists.

        HTTPException 500:
            If an unexpected database error occurs.
    """
    try:
        repo = CustomerRepository(db)
        customer = repo.create_customer(customer)

        return customer

    except IntegrityError as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "A customer with this email or phone number "
                "already exists."
            )
        ) from exc

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while creating the customer."
        ) from exc


@router.get(
    "/customers",
    response_model=list[CustomerResponse],
    status_code=status.HTTP_200_OK
)
def get_customers(
    db: Session = Depends(get_db)
):
    """
    Retrieve all customers from the database.

    Args:
        db: SQLAlchemy database session.

    Returns:
        list[CustomerResponse]: A list of all customers.

    Raises:
        HTTPException 404:
            If no customers are found.

        HTTPException 500:
            If an unexpected database error occurs.
    """
    try:
        repo = CustomerRepository(db)
        customers = repo.get_customers()

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving customers."
        ) from exc

    if not customers:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No customers found."
        )

    return customers
