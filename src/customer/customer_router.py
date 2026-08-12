"""
API routes for Customer operations.

This module handles HTTP requests and responses for customers.
Database operations are delegated to the CustomerRepository.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_db
from customer.customer_model import Customer
from customer.customer_repository import CustomerRepository


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

    Args:
        customer: Customer data submitted in the request.
        db: SQLAlchemy database session provided by FastAPI.

    Returns:
        The newly created customer.

    Raises:
        HTTPException 409:
            A customer with the provided email or phone number
            already exists.

        HTTPException 500:
            An unexpected database error occurs while creating
            the customer.
    """
    try:
        repo = CustomerRepository(db)
        customer = repo.create_customer(customer)

        return customer

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A customer with this email or phone number already exists."
        )

    except Exception as e:
        db.rollback()

        print(f"ERROR CREATING CUSTOMER: {e}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while creating the customer."
        )


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

    Args:
        db: SQLAlchemy database session provided by FastAPI.

    Returns:
        A list of all customers.

    Raises:
        HTTPException 404:
            No customers exist in the database.

        HTTPException 500:
            An unexpected database error occurs while retrieving
            customers.
    """
    try:
        repo = CustomerRepository(db)
        customers = repo.get_customers()

    except Exception as e:
        print(f"ERROR RETRIEVING CUSTOMERS: {e}")

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
