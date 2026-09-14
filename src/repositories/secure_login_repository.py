"""
Repository layer responsible for employee authentication, credential
management, password hashing, and JWT token operations.
"""

from datetime import datetime, timedelta, timezone
import uuid

from jose import jwt
from sqlalchemy.orm import Session

from config import settings
from employee.employee_schema import EmployeeSchema
from repositories.employee_repository import EmployeeRepository
from exceptions.secure_login_exceptions import (
    CredentialsAlreadyExistError,
    EmployeeNotFoundError,
    IncorrectPasswordError,
    TokenBlacklistedError,
    TokenMissingClaimError,
    UsernameNotFoundError,
    UsernameTakenError,
)
from secure_login.secure_login_model import EmployeeAuthCreate
from secure_login.secure_login_schema import EmployeeAuth
from secure_logout.secure_logout_schema import TokenBlacklist
from utils.jwt_utils import decode_token, extract_jti
from utils.password_utils import hash_password, verify_password

SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


class SecureLoginRepository:
    """
    Repository providing authentication utilities, credential management,
    and JWT token operations for employee login functionality.
    """

    def hash_password(self, plain: str) -> str:
        """
        Hash a plaintext password using the shared password utility.
        """

        return hash_password(plain)

    def verify_password(
        self,
        plain: str,
        hashed: str,
    ) -> bool:
        """
        Verify a plaintext password against a stored bcrypt hash.
        """

        return verify_password(
            plain,
            hashed,
        )

    def authenticate_user(
        self,
        db: Session,
        username: str,
        password: str,
    ):
        """
        Authenticate a user by validating their username and password.
        """

        auth = (
            db.query(EmployeeAuth)
            .filter(
                EmployeeAuth.username == username
            )
            .first()
        )

        if auth is None:
            raise UsernameNotFoundError(username)

        if not verify_password(
            password,
            auth.password_hash,
        ):
            raise IncorrectPasswordError(username)

        return auth

    def create_access_token(self, data: dict) -> str:
        """
        Create a signed JWT access token containing the provided payload.
        """

        to_encode = data.copy()

        jti = uuid.uuid4().hex

        to_encode.update({
            "jti": jti,
        })

        expire = (
            datetime.now(timezone.utc)
            + timedelta(
                minutes=ACCESS_TOKEN_EXPIRE_MINUTES
            )
        )

        to_encode.update({
            "exp": expire,
        })

        return jwt.encode(
            to_encode,
            SECRET_KEY,
            algorithm=ALGORITHM,
        )

    def get_current_employee(
        self,
        token: str,
        db: Session,
    ):
        """
        Decode a JWT token and retrieve the associated employee record.
        """

        payload = decode_token(token)

        jti = extract_jti(payload)

        blacklisted = (
            db.query(TokenBlacklist)
            .filter(
                TokenBlacklist.token_signature == jti
            )
            .first()
        )

        if blacklisted:
            raise TokenBlacklistedError()

        employee_id = payload.get("employee_id")

        if employee_id is None:
            raise TokenMissingClaimError(
                "employee_id"
            )

        repo = EmployeeRepository(db)

        employee = repo.get_employee_by_id(
            employee_id
        )

        return employee

    def register_employee_auth(
        self,
        db: Session,
        data: EmployeeAuthCreate,
    ):
        """
        Register new login credentials for an existing employee.
        """

        employee = (
            db.query(EmployeeSchema)
            .filter(
                EmployeeSchema.id == data.employee_id
            )
            .first()
        )

        if employee is None:
            raise EmployeeNotFoundError(
                data.employee_id
            )

        if (
            db.query(EmployeeAuth)
            .filter(
                EmployeeAuth.username == data.username
            )
            .first()
        ):
            raise UsernameTakenError(
                data.username
            )

        if (
            db.query(EmployeeAuth)
            .filter(
                EmployeeAuth.employee_id == data.employee_id
            )
            .first()
        ):
            raise CredentialsAlreadyExistError(
                data.employee_id
            )

        new_auth = EmployeeAuth(
            employee_id=data.employee_id,
            role=employee.role.role,
            username=data.username,
            password_hash=self.hash_password(
                data.password
            ),
        )

        db.add(new_auth)
        db.commit()
        db.refresh(new_auth)

        return new_auth

    def change_password(
        self,
        db: Session,
        employee_id: int,
        current_password: str,
        new_password: str,
    ) -> None:
        """
        Change an employee's password.

        The current password must be verified before the new password
        is stored.
        """

        auth = (
            db.query(EmployeeAuth)
            .filter(
                EmployeeAuth.employee_id == employee_id
            )
            .first()
        )

        if auth is None:
            raise EmployeeNotFoundError(
                employee_id
            )

        if not verify_password(
            current_password,
            auth.password_hash,
        ):
            raise IncorrectPasswordError(
                auth.username
            )

        auth.password_hash = self.hash_password(
            new_password
        )

        auth.is_temporary_password = False

        db.commit()
        db.refresh(auth)
