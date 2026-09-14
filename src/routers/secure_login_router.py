"""
Authentication router providing login, identity retrieval, and credential
registration for employee accounts.
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from database import get_db
from repositories.secure_login_repository import SecureLoginRepository
from secure_login.secure_login_model import (
    EmployeeAuthCreate,
    PasswordChangeRequest,
)

from exceptions.secure_login_exceptions import (
    UsernameNotFoundError,
    IncorrectPasswordError,
    TokenExpiredError,
    TokenInvalidSignatureError,
    TokenDecodeError,
    TokenMissingClaimError,
    TokenBlacklistedError,
    EmployeeNotFoundError,
    UsernameTakenError,
    CredentialsAlreadyExistError,
)


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="auth/login",
)

auth_repo = SecureLoginRepository()


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Authenticate an employee and issue a JWT access token.

    The returned token includes the employee ID, role, and whether
    the employee must change their temporary password.
    """

    try:
        auth = auth_repo.authenticate_user(
            db,
            form_data.username,
            form_data.password,
        )

    except UsernameNotFoundError as exc:
        raise HTTPException(
            status_code=401,
            detail=str(exc),
        ) from exc

    except IncorrectPasswordError as exc:
        raise HTTPException(
            status_code=401,
            detail=str(exc),
        ) from exc

    employee = auth.employee

    token = auth_repo.create_access_token(
        {
            "employee_id": employee.id,
            "role": employee.role.role,
            "must_change_password": auth.is_temporary_password,
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "must_change_password": auth.is_temporary_password,
    }


@router.post("/password/change")
def change_password(
    data: PasswordChangeRequest,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """
    Change the authenticated employee's password.

    The JWT must be valid and must not have been revoked.
    """

    try:
        employee = auth_repo.get_current_employee(
            token,
            db,
        )

        auth_repo.change_password(
            db,
            employee.id,
            data.current_password,
            data.new_password,
        )

    except (
        TokenExpiredError,
        TokenInvalidSignatureError,
        TokenDecodeError,
        TokenMissingClaimError,
        TokenBlacklistedError,
        EmployeeNotFoundError,
    ) as exc:
        raise HTTPException(
            status_code=401,
            detail=str(exc),
        ) from exc

    except IncorrectPasswordError as exc:
        raise HTTPException(
            status_code=401,
            detail=str(exc),
        ) from exc

    return {
        "message": "Password changed successfully"
    }


@router.get("/me")
def get_current_employee(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """
    Retrieve the currently authenticated employee.

    The JWT must be valid, contain the required employee ID and JTI
    claims, and must not have been revoked.
    """

    try:
        employee = auth_repo.get_current_employee(
            token,
            db,
        )

    except TokenExpiredError as exc:
        raise HTTPException(
            status_code=401,
            detail=str(exc),
        ) from exc

    except TokenInvalidSignatureError as exc:
        raise HTTPException(
            status_code=401,
            detail=str(exc),
        ) from exc

    except TokenDecodeError as exc:
        raise HTTPException(
            status_code=401,
            detail=str(exc),
        ) from exc

    except TokenMissingClaimError as exc:
        raise HTTPException(
            status_code=401,
            detail=str(exc),
        ) from exc

    except TokenBlacklistedError as exc:
        raise HTTPException(
            status_code=401,
            detail=str(exc),
        ) from exc

    except EmployeeNotFoundError as exc:
        raise HTTPException(
            status_code=401,
            detail=str(exc),
        ) from exc

    return employee


@router.post("/register")
def register_employee_auth(
    data: EmployeeAuthCreate,
    db: Session = Depends(get_db),
):
    """
    Register login credentials for an existing employee.
    """

    try:
        auth_repo.register_employee_auth(
            db,
            data,
        )

    except EmployeeNotFoundError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except UsernameTakenError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except CredentialsAlreadyExistError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return {
        "message": "Login credentials created successfully"
    }
