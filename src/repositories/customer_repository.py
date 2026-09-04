"""
Repository layer for Customer database operations.

This module contains the database logic used to create, retrieve, and
update customer records, including duplicate-detection and not-found
business rules. API-specific logic, such as HTTP status codes and
HTTP exceptions, belongs in the router layer — this module raises typed
domain exceptions instead.
"""


from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from customer.customer_model import CustomerCreate, CustomerUpdate
from customer.customer_schema import CustomerSchema
from exceptions.customer_exceptions import (
    CustomerConstraintError,
    CustomerEmailAlreadyExistsError,
    CustomerNotFoundError,
    CustomerPhoneAlreadyExistsError,
)
from utils.error_utils import parse_integrity_error


class CustomerRepository:
    """
    Repository for customer database operations.

    This class handles creating, retrieving, and updating customer
    records using a SQLAlchemy database session.
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

    def update_customer(
        self,
        customer_id: int,
        customer: CustomerUpdate
    ) -> CustomerSchema:
        """
        Update and persist an existing customer's properties.

        Args:
            customer_id: The ID of the customer to update.
            customer: CustomerUpdate object containing the validated
                replacement customer data.

        Returns:
            CustomerSchema: The updated customer record.

        Raises:
            CustomerNotFoundError:
                If no customer exists with the given ID.
            CustomerEmailAlreadyExistsError:
                If another customer already has the given email.
            CustomerPhoneAlreadyExistsError:
                If another customer already has the given phone
                number.
            CustomerConstraintError:
                If the update violates another database constraint.
        """
        db_customer = self.get_customer_by_id(customer_id)
        if db_customer is None:
            raise CustomerNotFoundError(customer_id)

        existing_email = self.get_customer_by_email(customer.email)
        if existing_email and existing_email.id != customer_id:
            raise CustomerEmailAlreadyExistsError(customer.email)

        existing_phone = self.get_customer_by_phone(
            customer.phone_number
        )
        if existing_phone and existing_phone.id != customer_id:
            raise CustomerPhoneAlreadyExistsError(customer.phone_number)

        db_customer.active = customer.active
        db_customer.first_name = customer.first_name
        db_customer.last_name = customer.last_name
        db_customer.email = customer.email
        db_customer.phone_number = customer.phone_number
        db_customer.loyalty_points = customer.loyalty_points

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

    def deactivate_customer(self, customer_id: int) -> None:
        """
        Deactivate a customer by setting active to False (soft delete).

        The customer record is preserved for historical purposes;
        only its active status is updated.

        Args:
            customer_id: The ID of the customer to deactivate.

        Raises:
            CustomerNotFoundError:
                If no customer exists with the given ID.
        """
        db_customer = self.get_customer_by_id(customer_id)

        db_customer.active = False

        self.db.commit()

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
