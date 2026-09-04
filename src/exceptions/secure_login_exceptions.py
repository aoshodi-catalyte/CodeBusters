"""
Custom exception classes used for secure login and authentication operations.

These exceptions allow the repository layer to raise clear, typed errors
that the router can catch and translate into appropriate HTTP responses,
rather than relying on generic Exception handling or building HTTPException
objects directly in business logic.
"""


class UsernameNotFoundError(Exception):
    """Raised when a username does not exist in the system."""

    def __init__(self, username: str) -> None:
        self.username = username
        super().__init__(f"Username '{username}' does not exist.")


class IncorrectPasswordError(Exception):
    """Raised when a password does not match the stored hash."""

    def __init__(self, username: str) -> None:
        self.username = username
        super().__init__(f"Incorrect password for username '{username}'.")


class TokenExpiredError(Exception):
    """Raised when a JWT token has expired."""

    def __init__(self) -> None:
        super().__init__("Token has expired.")


class TokenInvalidSignatureError(Exception):
    """Raised when a JWT token's signature is invalid."""

    def __init__(self) -> None:
        super().__init__("Token signature is invalid.")


class TokenDecodeError(Exception):
    """Raised when a JWT token is malformed or cannot be decoded."""

    def __init__(self, message: str | None = None) -> None:
        self.message = message
        super().__init__(message or "Token is malformed or cannot be decoded.")


class TokenMissingClaimError(Exception):
    """Raised when a required claim is missing from the JWT token."""

    def __init__(self, claim: str) -> None:
        self.claim = claim
        super().__init__(f"Token is missing required claim: '{claim}'.")


class EmployeeNotFoundError(Exception):
    """Raised when the employee referenced in the token does not exist."""

    def __init__(self, employee_id: int) -> None:
        self.employee_id = employee_id
        super().__init__(f"Employee with ID {employee_id} does not exist.")


class UsernameTakenError(Exception):
    """Raised when attempting to register a username that is already taken."""

    def __init__(self, username: str) -> None:
        self.username = username
        super().__init__(f"Username '{username}' is already taken.")


class CredentialsAlreadyExistError(Exception):
    """Raised when an employee already has login credentials."""

    def __init__(self, employee_id: int) -> None:
        self.employee_id = employee_id
        super().__init__(
            f"Employee with ID {employee_id} already has login credentials."
        )


class TokenBlacklistedError(Exception):
    """Raised when a JWT token has been revoked and is no longer valid."""

    def __init__(self) -> None:
        super().__init__("Token has been revoked and is no longer valid.")
