"""
Custom exception classes used for customer-related operations.

These exceptions allow the repository layer to raise clear, typed errors
that the router can catch and translate into appropriate HTTP responses,
rather than relying on generic Exception handling or building HTTPException
objects directly in business logic.
"""


class CustomerNotFoundError(Exception):
    """Raised when a customer with the given ID does not exist."""

    def __init__(self, customer_id: int) -> None:
        self.customer_id = customer_id
        super().__init__(f"Customer with ID {customer_id} was not found.")


class CustomerEmailAlreadyExistsError(Exception):
    """Raised when a customer with the given email already exists."""

    def __init__(self, email: str) -> None:
        self.email = email
        super().__init__(
            f"A customer with the email '{email}' already exists."
        )


class CustomerPhoneAlreadyExistsError(Exception):
    """Raised when a customer with the given phone number already exists."""

    def __init__(self, phone_number: str) -> None:
        self.phone_number = phone_number
        super().__init__(
            f"A customer with the phone number '{phone_number}' "
            "already exists."
        )


class CustomerConstraintError(Exception):
    """Raised when a customer record violates a database constraint."""

    def __init__(self, constraint: str | None = None) -> None:
        self.constraint = constraint
        super().__init__(
            "The customer record violates a database constraint."
        )
