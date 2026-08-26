"""
Repository layer for Customer database operations.

This module contains the database logic used to create and retrieve
customer records, including duplicate-detection and not-found business
rules. API-specific logic, such as HTTP status codes and HTTP
exceptions, belongs in the router layer — this module raises typed
domain exceptions instead.
"""


from customer.customer_model import CustomerCreate
from customer.customer_schema import CustomerSchema
from exceptions.customer_exceptions import (
    CustomerConstraintError,
    CustomerEmailAlreadyExistsError,
    CustomerNotFoundError,
    CustomerPhoneAlreadyExistsError,
)
from utils.error_utils import parse_integrity_error
from sqlalchemy.orm import Session


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

        Raises:
            CustomerEmailAlreadyExistsError:
                If a customer with the same email already exists.
            CustomerPhoneAlreadyExistsError:
                If a customer with the same phone number already
                exists.
            CustomerConstraintError:
                If the record violates another database constraint.
        """
        if self.get_customer_by_email(customer.email):
            raise CustomerEmailAlreadyExistsError(customer.email)

        if self.get_customer_by_phone(customer.phone_number):
            raise CustomerPhoneAlreadyExistsError(customer.phone_number)

        db_customer = CustomerSchema(
            first_name=customer.first_name,
            last_name=customer.last_name,
            email=customer.email,
            phone_number=customer.phone_number,
            active=customer.active,
            loyalty_points=customer.loyalty_points
        )

        self.db.add(db_customer)

        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            constraint, error_message = parse_integrity_error(exc)

            if "email" in error_message:
                raise CustomerEmailAlreadyExistsError(
                    customer.email
                ) from exc

            if "phone" in error_message:
                raise CustomerPhoneAlreadyExistsError(
                    customer.phone_number
                ) from exc

            raise CustomerConstraintError(constraint) from exc

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

    def get_customer_by_id(
        self,
        customer_id: int
    ) -> CustomerSchema:
        """
        Retrieve a customer by its ID.

        Args:
            customer_id: The ID of the customer to retrieve.

        Returns:
            CustomerSchema: The matching customer.

        Raises:
            CustomerNotFoundError:
                If no customer exists with the given ID.
        """
        customer = (
            self.db.query(CustomerSchema)
            .filter(CustomerSchema.id == customer_id)
            .first()
        )

        if customer is None:
            raise CustomerNotFoundError(customer_id)

        return customer

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
