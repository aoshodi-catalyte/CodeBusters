"""
Repository layer responsible for employee authentication, credential
management, password hashing, and JWT token operations.
"""

from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from jose import ExpiredSignatureError, jwt, JWTError  # type: ignore

from exceptions.secure_login_exceptions import (
    UsernameNotFoundError,
    IncorrectPasswordError,
    TokenExpiredError,
    TokenInvalidSignatureError,
    TokenDecodeError,
    TokenMissingClaimError,
    EmployeeNotFoundError,
    UsernameTakenError,
    CredentialsAlreadyExistError,
)

from passlib.context import CryptContext  # type: ignore

from secure_login.secure_login_schema import EmployeeAuth
from secure_login.secure_login_model import EmployeeAuthCreate
from employee.employee_schema import EmployeeSchema
from config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


class SecureLoginRepository:
    """
    Repository providing authentication utilities, credential management,
    and JWT token operations for employee login functionality.

    This class encapsulates all security‑related logic, keeping the API
    router lightweight and focused on HTTP concerns.
    """

    def hash_password(self, plain: str) -> str:
        """
        Hash a plaintext password.

        This method is responsible for converting a plaintext password into a
        secure, stored representation. The current implementation is a stub
        and should be replaced with a proper hashing algorithm (e.g., bcrypt)
        in production environments.

        Args:
            plain (str):
                The plaintext password provided during registration.

        Returns:
            str:
                A hashed password string suitable for storage.
        """

        return plain

    def verify_password(self, plain: str, hashed: str) -> bool:
        """
        Verify a plaintext password against a stored hash.

        This method checks whether the provided plaintext password matches the
        stored hashed password. The current implementation performs a direct
        comparison and should be replaced with a secure hash verification
        algorithm (e.g., bcrypt) in production environments.

        Args:
            plain (str):
                The plaintext password provided during login.
            hashed (str):
                The stored hashed password retrieved from the database.

        Returns:
            bool:
                True if the password matches, otherwise False.
        """

        return plain == hashed

    def authenticate_user(self, db: Session, username: str, password: str):
        """
        Authenticate a user by validating their username and password.

        This method retrieves the authentication record associated with the
        provided username and verifies the supplied password. Typed exceptions
        are raised for specific authentication failures, allowing the router
        to translate them into precise HTTP responses:

        - UsernameNotFoundError:
            Raised when the username does not exist in the system.
        - IncorrectPasswordError:
            Raised when the password does not match the stored hash.

        Args:
            db (Session):
                Active database session.
            username (str):
                The username provided during login.
            password (str):
                The plaintext password provided during login.

        Returns:
            EmployeeAuth:
                The authenticated employee's credential record.

        Raises:
            UsernameNotFoundError:
                If the username does not exist.
            IncorrectPasswordError:
                If the password is incorrect.
        """

        auth = db.query(EmployeeAuth).filter(EmployeeAuth.username == username).first()

        if auth is None:
            raise UsernameNotFoundError(username)

        if not self.verify_password(password, auth.password_hash):
            raise IncorrectPasswordError(username)

        return auth

    def create_access_token(self, data: dict) -> str:
        """
        Create a signed JWT access token containing the provided payload.

        This method generates a JWT token used for authenticating subsequent
        requests. The token includes an expiration timestamp (`exp`) and any
        additional claims supplied in the payload. The token is signed using
        the application's configured secret key and algorithm.

        Args:
            data (dict):
                A dictionary of claims to embed in the token. Common fields
                include `employee_id` and `role`.

        Returns:
            str:
                A signed JWT token string suitable for use in Authorization
                headers.
        """

        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    def get_current_employee(self, token: str, db: Session):
        """
        Decode a JWT token and retrieve the associated employee record.

        This method validates and decodes the provided JWT token. Typed
        exceptions are raised for specific token validation failures, allowing
        the router to translate them into precise HTTP responses:

        Args:
            token (str):
                The JWT access token provided by the client.
            db (Session):
                Active database session.

        Returns:
            EmployeeSchema:
                The employee associated with the token.

        Raises:
            TokenExpiredError:
                If the token has expired.
            TokenInvalidSignatureError:
                If the token signature is invalid.
            TokenDecodeError:
                If the token is malformed.
            TokenMissingClaimError:
                If required claims are missing.
            EmployeeNotFoundError:
                If the referenced employee does not exist.
        """

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        except ExpiredSignatureError as exc:
            raise TokenExpiredError() from exc

        except JWTError as exc:
            msg = str(exc).lower()

            if "signature" in msg or "invalid signature" in msg:
                raise TokenInvalidSignatureError() from exc

            raise TokenDecodeError(msg) from exc

        employee_id = payload.get("employee_id")
        if employee_id is None:
            raise TokenMissingClaimError("employee_id")

        employee = (
            db.query(EmployeeSchema).filter(EmployeeSchema.id == employee_id).first()
        )

        if employee is None:
            raise EmployeeNotFoundError(employee_id)

        return employee

    def register_employee_auth(self, db: Session, data: EmployeeAuthCreate):
        """
        Register new login credentials for an existing employee.

        This method validates the credential creation request by ensuring the
        employee exists, the username is not already taken, and the employee
        does not already have login credentials. Typed exceptions are raised
        for specific validation failures:

        Args:
            db (Session):
                Active database session.
            data (EmployeeAuthCreate):
                Payload containing employee ID, username, and password.

        Returns:
            EmployeeAuth:
                The newly created authentication record.

        Raises:
            EmployeeNotFoundError:
                If the employee does not exist.
            UsernameTakenError:
                If the username is already taken.
            CredentialsAlreadyExistError:
                If the employee already has credentials.
        """

        employee = (
            db.query(EmployeeSchema)
            .filter(EmployeeSchema.id == data.employee_id)
            .first()
        )

        if employee is None:
            raise EmployeeNotFoundError(data.employee_id)

        if (
            db.query(EmployeeAuth)
            .filter(EmployeeAuth.username == data.username)
            .first()
        ):
            raise UsernameTakenError(data.username)

        if (
            db.query(EmployeeAuth)
            .filter(EmployeeAuth.employee_id == data.employee_id)
            .first()
        ):
            raise CredentialsAlreadyExistError(data.employee_id)

        new_auth = EmployeeAuth(
            employee_id=data.employee_id,
            username=data.username,
            password_hash=self.hash_password(data.password),
        )

        db.add(new_auth)
        db.commit()
        db.refresh(new_auth)

        return new_auth
