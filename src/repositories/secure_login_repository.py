"""
Repository layer responsible for employee authentication, credential
management, password hashing, and JWT token operations.
"""

from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from jose import jwt, JWTError  # type: ignore
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

    def hash_password(self, password: str) -> str:
        """
        Hash a plaintext password using bcrypt.

        Args:
            password (str):
                The plaintext password to hash.

        Returns:
            str: A securely hashed password string.
        """

        return pwd_context.hash(password)

    def verify_password(self, plain: str, hashed: str) -> bool:
        """
        Verify a plaintext password against a stored bcrypt hash.

        Args:
            plain (str):
                The plaintext password provided by the user.
            hashed (str):
                The stored hashed password retrieved from the database.

        Returns:
            bool: True if the password matches, otherwise False.
        """

        return pwd_context.verify(plain, hashed)

    def authenticate_user(self, db: Session, username: str, password: str):
        """
        Authenticate a user by validating their username and password.

        A dummy password verification is performed when the username does
        not exist to mitigate timing attacks.

        Args:
            db (Session):
                Active database session.
            username (str):
                Username provided during login.
            password (str):
                Password provided during login.

        Returns:
            EmployeeAuth | None:
                The authenticated user record, or None if authentication fails.
        """

        auth = db.query(EmployeeAuth).filter(EmployeeAuth.username == username).first()

        if not auth:
            self.verify_password(password, self.hash_password("dummy"))
            return None

        if not self.verify_password(password, auth.password_hash):
            return None

        return auth

    def create_access_token(self, data: dict) -> str:
        """
        Create a signed JWT access token containing the provided payload.

        Args:
            data (dict):
                The payload to encode into the JWT token.

        Returns:
            str: A signed JWT token string.
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

        Args:
            token (str):
                The JWT access token provided by the client.
            db (Session):
                Active database session.

        Returns:
            EmployeeSchema | None:
                The employee associated with the token, or None if not found.

        Raises:
            ValueError:
                If the token is invalid or expired.
        """

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            employee_id: int = payload.get("employee_id")
        except JWTError as exc:
            raise ValueError("Invalid or expired token") from exc

        employee = (
            db.query(EmployeeSchema).filter(EmployeeSchema.id == employee_id).first()
        )
        return employee

    def register_employee_auth(self, db: Session, data: EmployeeAuthCreate):
        """
        Register new login credentials for an existing employee.

        Validation includes:
        - Ensuring the employee exists
        - Ensuring the username is not already taken
        - Ensuring the employee does not already have login credentials

        Args:
            db (Session):
                Active database session.
            data (EmployeeAuthCreate):
                Payload containing employee ID, username, and password.

        Returns:
            EmployeeAuth:
                The newly created authentication record.

        Raises:
            ValueError:
                If validation fails (employee not found, username taken,
                or credentials already exist).
        """

        employee = (
            db.query(EmployeeSchema)
            .filter(EmployeeSchema.id == data.employee_id)
            .first()
        )
        if not employee:
            raise ValueError("Employee not found")

        existing_username = (
            db.query(EmployeeAuth)
            .filter(EmployeeAuth.username == data.username)
            .first()
        )
        if existing_username:
            raise ValueError("Username already taken")

        existing_auth = (
            db.query(EmployeeAuth)
            .filter(EmployeeAuth.employee_id == data.employee_id)
            .first()
        )
        if existing_auth:
            raise ValueError("Employee already has login credentials")

        hashed_pw = self.hash_password(data.password)

        auth_record = EmployeeAuth(
            employee_id=data.employee_id,
            role=employee.role.role,
            username=data.username,
            password_hash=hashed_pw,
        )

        db.add(auth_record)
        db.commit()
        db.refresh(auth_record)

        return auth_record
