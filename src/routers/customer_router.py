"""
API routes for Customer operations.

This module handles all HTTP requests and responses for customers.
Database operations are delegated to the customer repository.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_db
from customer.customer_model import CustomerCreate, CustomerResponse
from repositories.customer_repository import CustomerRepository


router = APIRouter()


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

    Raises:
        HTTPException 409:
            If the email already exists.

        HTTPException 409:
            If the phone number already exists.

        HTTPException 500:
            If an unexpected database error occurs.
    """
    try:
        repo = CustomerRepository(db)

        # Check if the email already exists
        existing_email = repo.get_customer_by_email(customer.email)

        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A customer with this email already exists."
            )

        # Check if the phone number already exists
        existing_phone = repo.get_customer_by_phone(
            customer.phone_number
        )

        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A customer with this phone number already exists."
            )

        new_customer = repo.create_customer(customer)

        return new_customer

    except HTTPException:
        raise

    except IntegrityError as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A duplicate customer record already exists."
        ) from exc

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "An unexpected error occurred while creating "
                "the customer."
            )
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
        list[CustomerResponse]: A list of all customers. Returns an
        empty list when no customers are found.

    Raises:
        HTTPException 500:
            If an unexpected database error occurs.
    """
    try:
        repo = CustomerRepository(db)
        customers = repo.get_customers()

        return customers

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "An unexpected error occurred while retrieving "
                "customers."
            )
        ) from exc


@router.get(
    "/customers/{customer_id}",
    response_model=CustomerResponse,
    status_code=status.HTTP_200_OK
)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieve a single customer by ID.

    Args:
        customer_id: The ID of the customer to retrieve.
        db: SQLAlchemy database session.

    Returns:
        CustomerResponse: The customer matching the provided ID.

    Raises:
        HTTPException 404:
            If no customer exists with the provided ID.

        HTTPException 500:
            If an unexpected database error occurs.
    """
    try:
        repo = CustomerRepository(db)
        customer = repo.get_customer_by_id(customer_id)

        if customer is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"Customer with ID {customer_id} was not found."
                )
            )

        return customer

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "An unexpected error occurred while retrieving "
                "the customer."
            )
        ) from exc
