"""
Authentication router providing login, identity retrieval, and credential
registration for employee accounts.
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from database import get_db
from repositories.secure_login_repository import SecureLoginRepository
from secure_login.secure_login_model import EmployeeAuthCreate

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

router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

auth_repo = SecureLoginRepository()


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Authenticate an employee and issue a JWT access token.

    This endpoint validates the provided username and password using the
    authentication repository. If authentication succeeds, a signed JWT
    token containing the employee ID and role is returned. The token can
    be used to authorize subsequent requests to protected endpoints.

    Authentication failures raise typed exceptions from the repository,
    which are translated into HTTP 401 responses:

    - UsernameNotFoundError:
        Raised when the provided username does not exist.
    - IncorrectPasswordError:
        Raised when the password does not match the stored hash.

    Args:
        form_data (OAuth2PasswordRequestForm):
            The OAuth2 login form containing `username` and `password`.
        db (Session):
            Database session dependency.

    Returns:
        dict:
            A dictionary containing:
            - `access_token`: The signed JWT token.
            - `token_type`: Always `"bearer"`.

    Raises:
        HTTPException (401):
            If the username does not exist or the password is incorrect.
    """

    try:
        auth = auth_repo.authenticate_user(db, form_data.username, form_data.password)

    except UsernameNotFoundError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc

    except IncorrectPasswordError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc

    employee = auth.employee

    token = auth_repo.create_access_token(
        {"employee_id": employee.id, "role": employee.role.role}
    )

    return {"access_token": token, "token_type": "bearer"}


@router.get("/me")
def get_current_employee(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """
    Retrieve the currently authenticated employee based on the provided JWT token.

    This endpoint decodes and validates the JWT access token using the
    authentication repository. If the token is valid and the referenced
    employee exists, the corresponding employee record is returned.

    Args:
        token (str):
            The JWT access token extracted from the Authorization header.
        db (Session):
            Database session dependency.

    Returns:
        EmployeeSchema:
            The authenticated employee record.

    Raises:
        HTTPException (401):
            If the token is invalid, expired, malformed, missing claims,
            or references a non‑existent employee.
    """
    try:
        employee = auth_repo.get_current_employee(token, db)

    except TokenExpiredError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc

    except TokenInvalidSignatureError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc

    except TokenDecodeError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc

    except TokenMissingClaimError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc

    except EmployeeNotFoundError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc

    return employee


@router.post("/register")
def register_employee_auth(
    data: EmployeeAuthCreate,
    db: Session = Depends(get_db),
):
    """
    Register login credentials for an existing employee.

    This endpoint delegates credential creation to the authentication
    repository. Validation includes ensuring the employee exists, the
    username is not already taken, and the employee does not already
    have login credentials. If validation succeeds, a new authentication
    record is created and persisted.

    Args:
        data (EmployeeAuthCreate):
            Payload containing employee ID, username, and password.
        db (Session):
            Database session dependency.

    Returns:
        dict:
            A confirmation message indicating successful credential creation.

    Raises:
        HTTPException (400):
            If the employee does not exist, the username is taken, or the
            employee already has credentials.
    """

    try:
        auth_repo.register_employee_auth(db, data)

    except EmployeeNotFoundError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    except UsernameTakenError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    except CredentialsAlreadyExistError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {"message": "Login credentials created successfully"}
