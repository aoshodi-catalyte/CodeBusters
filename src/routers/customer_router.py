"""
API routes for Customer operations.

This module handles all HTTP requests and responses for customers.
Database operations and business rules (duplicate detection, not-found
handling) are delegated to the customer repository, which raises typed
exceptions on failure.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from customer.customer_model import CustomerCreate, CustomerResponse, CustomerUpdate
from database import get_audit_db, get_db
from exceptions.customer_exceptions import (
    CustomerAlreadyDeactivatedError,
    CustomerConstraintError,
    CustomerEmailAlreadyExistsError,
    CustomerNotFoundError,
    CustomerPhoneAlreadyExistsError,
)
from repositories.customer_repository import CustomerRepository
from repositories.deactivate_audit_repository import AuditRepository
from security.secure_manager_login import check_role
from utils.auth import get_acting_user
from utils.error_handlers import handle_repo_exception


router = APIRouter()


@router.post(
    "/customers",
    dependencies=[Depends(check_role(["manager"]))],
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

# pylint: disable=duplicate-code

    except (
        CustomerEmailAlreadyExistsError,
        CustomerPhoneAlreadyExistsError,
        CustomerConstraintError,
    ) as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

# pylint: enable=duplicate-code


@router.put(
    "/customers/{customer_id}",
    dependencies=[Depends(check_role(["manager"]))],
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

# pylint: disable=duplicate-code

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

# pylint: enable=duplicate-code


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


@router.delete(
    "/customers/{customer_id}",
    dependencies=[Depends(check_role(["manager"]))],
    status_code=status.HTTP_204_NO_CONTENT,
)
def deactivate_customer(
    customer_id: int,
    acting_user = Depends(get_acting_user),
    db: Session = Depends(get_db),
    audit_db: Session = Depends(get_audit_db),
):
    """
    Deactivate a customer (soft delete) by setting active to False.

    The customer's record is preserved for historical purposes.

    Raises:
        HTTPException 404:
            If no customer exists with the provided ID.
    """

    repo = CustomerRepository(db)
    audit_repo = AuditRepository(audit_db)

    try:
        repo.deactivate_customer(customer_id, acting_user.email, audit_repo)
    except Exception as e:
        handle_repo_exception(
            db,
            e,
            CustomerNotFoundError(customer_id),
            CustomerAlreadyDeactivatedError(customer_id)
        )
