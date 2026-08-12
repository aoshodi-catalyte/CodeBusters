
"""
Repository layer for Customer database operations.

This module contains the database logic used to create and
retrieve customer records. API-specific logic such as HTTP
status codes and HTTP exceptions belongs in the router.
"""

from sqlalchemy.orm import Session

from customer.customer_schema import CustomerSchema


def create_customer(
    db: Session,
    customer: CustomerSchema
) -> CustomerSchema:
    """
    Creates and persists a customer in the database.

    Args:
        db: SQLAlchemy database session.
        customer: Customer SQLAlchemy model to persist.

    Returns:
        The newly created customer with its generated ID.
    """

    db.add(customer)
    db.commit()
    db.refresh(customer)

    return customer


def get_customers(
    db: Session
) -> list[CustomerSchema]:
    """
    Retrieves all customers from the database.

    Args:
        db: SQLAlchemy database session.

    Returns:
        A list of all customer records.
    """

    return db.query(CustomerSchema).all()

