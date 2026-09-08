"""
Custom exception classes used for employee-related operations.

These exceptions allow the repository layer to raise clear, typed errors
that the router can catch and translate into appropriate HTTP responses,
rather than relying on generic Exception handling.
"""


class EmployeeEmailAlreadyExistsError(Exception):
    """Raised when a employee with the given email already exists."""

    def __init__(self, email: str) -> None:
        self.email = email
        super().__init__(
            f"A employee with the email '{email}' already exists."
        )
