"""
API routes for Customer operations.

This module handles HTTP requests and responses for customers.
Database operations are delegated to the customer repository.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_db
from customer.customer_model import CustomerCreate, CustomerResponse
from customer.customer_repository import CustomerRepository


logger = logging.getLogger(__name__)

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

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "A customer with this email or phone number "
                "already exists."
            )
        )

    except Exception as e:
        db.rollback()

        logger.error(
            "Error creating customer: %s",
            e
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while creating the customer."
        )


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

        if not customers:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No customers found."
            )

        return customers

    except HTTPException:
        raise

    except Exception as e:
        logger.error(
            "Error retrieving customers: %s",
            e
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving customers."
        )