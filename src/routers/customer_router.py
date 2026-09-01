"""
API routes for Customer operations.

This module handles all HTTP requests and responses for customers.
Database operations and business rules (duplicate detection, not-found
handling) are delegated to the customer repository, which raises typed
exceptions on failure.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from exceptions.customer_exceptions import (
    CustomerConstraintError,
    CustomerEmailAlreadyExistsError,
    CustomerNotFoundError,
    CustomerPhoneAlreadyExistsError,
)
from customer.customer_model import (
    CustomerCreate,
    CustomerResponse,
    CustomerUpdate,
)
from database import get_db
from repositories.customer_repository import CustomerRepository


router = APIRouter()


@router.post(
    "/customers",
    response_model=CustomerResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_customer(
    customer: CustomerCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new customer and persist it to the database.

    Raises:
        HTTPException 409:
            If the email or phone number already exists, or the record
            violates another database constraint.
    """
    repo = CustomerRepository(db)

    try:
        return repo.create_customer(customer)

    except (
        CustomerEmailAlreadyExistsError,
        CustomerPhoneAlreadyExistsError,
        CustomerConstraintError,
    ) as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.put(
    "/customers/{customer_id}",
    response_model=CustomerResponse,
    status_code=status.HTTP_200_OK,
)
def update_customer(
    customer_id: int,
    customer: CustomerUpdate,
    db: Session = Depends(get_db),
):
    """
    Update an existing customer's properties.

    Raises:
        HTTPException 404:
            If no customer exists with the provided ID.
        HTTPException 409:
            If the updated email or phone number belongs to another
            customer, or the record violates another database
            constraint.
    """
    repo = CustomerRepository(db)

    try:
        return repo.update_customer(customer_id, customer)

    except CustomerNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except (
        CustomerEmailAlreadyExistsError,
        CustomerPhoneAlreadyExistsError,
        CustomerConstraintError,
    ) as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.get(
    "/customers",
    response_model=list[CustomerResponse],
    status_code=status.HTTP_200_OK,
)
def get_customers(
    db: Session = Depends(get_db),
):
    """
    Retrieve all customers from the database.

    Returns:
        list[CustomerResponse]: A list of all customers. Returns an
        empty list when no customers are found.
    """
    repo = CustomerRepository(db)
    return repo.get_customers()


@router.get(
    "/customers/{customer_id}",
    response_model=CustomerResponse,
    status_code=status.HTTP_200_OK,
)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
):
    """
    Retrieve a single customer by ID.

    Raises:
        HTTPException 404:
            If no customer exists with the provided ID.
    """
    repo = CustomerRepository(db)

    try:
        return repo.get_customer_by_id(customer_id)

    except CustomerNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
