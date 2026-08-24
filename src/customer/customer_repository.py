"""
Repository layer for Customer database operations.

This module contains the database logic used to create and retrieve
customer records. API-specific logic, such as HTTP status codes and
HTTP exceptions, belongs in the router layer.
"""

from sqlalchemy.orm import Session

from customer.customer_model import CustomerCreate
from customer.customer_schema import CustomerSchema


class CustomerRepository:
    """
    Repository for customer database operations.

    This class handles creating and retrieving customer records
    using a SQLAlchemy database session.
    """

    def __init__(self, db: Session):
        """
        Initialize the customer repository with a database session.

        Args:
            db: SQLAlchemy database session used for customer
                database operations.
        """
        self.db = db

    def create_customer(
        self,
        customer: CustomerCreate
    ) -> CustomerSchema:
        """
        Create and persist a new customer in the database.

        Args:
            customer: CustomerCreate object containing the validated
                customer data.

        Returns:
            CustomerSchema: The newly created customer record,
                including its generated database ID.
        """
        db_customer = CustomerSchema(
            first_name=customer.first_name,
            last_name=customer.last_name,
            email=customer.email,
            phone_number=customer.phone_number,
            active=customer.active,
            loyalty_points=customer.loyalty_points
        )

        self.db.add(db_customer)
        self.db.commit()
        self.db.refresh(db_customer)

        return db_customer

    def get_customers(self) -> list[CustomerSchema]:
        """
        Retrieve all customers from the database.

        Returns:
            list[CustomerSchema]: A list containing all customer
            records. Returns an empty list when no customers exist.
        """
        return self.db.query(CustomerSchema).all()

    def get_customer_by_email(
        self,
        email: str
    ) -> CustomerSchema | None:
        """
        Retrieve a customer by email address.

        Args:
            email: The email address to search for.

        Returns:
            CustomerSchema | None: The matching customer if found,
            otherwise None.
        """
        return (
            self.db.query(CustomerSchema)
            .filter(CustomerSchema.email == email)
            .first()
        )

    def get_customer_by_phone(
        self,
        phone_number: str
    ) -> CustomerSchema | None:
        """
        Retrieve a customer by phone number.

        Args:
            phone_number: The phone number to search for.

        Returns:
            CustomerSchema | None: The matching customer if found,
            otherwise None.
        """
        return (
            self.db.query(CustomerSchema)
            .filter(CustomerSchema.phone_number == phone_number)
            .first()
        )
