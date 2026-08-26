"""
Authentication router providing login, identity retrieval, and credential
registration for employee accounts.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from database import get_db
from repositories.secure_login_repository import SecureLoginRepository
from secure_login.secure_login_model import EmployeeAuthCreate

router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

auth_repo = SecureLoginRepository()


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Authenticate an employee and return a JWT access token.

    This endpoint validates the provided username and password using the
    authentication repository. If authentication succeeds, a signed JWT
    token containing the employee ID and role is returned.

    Args:
        form_data (OAuth2PasswordRequestForm):
            The OAuth2 login form containing username and password.
        db (Session):
            Database session dependency.

    Returns:
        dict: A dictionary containing the access token and token type.

    Raises:
        HTTPException:
            - 401: If the username or password is invalid.
    """

    auth = auth_repo.authenticate_user(db, form_data.username, form_data.password)

    if not auth:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

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
    Retrieve the currently authenticated employee based on the JWT token.

    The token is decoded using the authentication repository. If valid,
    the corresponding employee record is returned.

    Args:
        token (str):
            The JWT access token extracted from the Authorization header.
        db (Session):
            Database session dependency.

    Returns:
        EmployeeSchema: The authenticated employee record.

    Raises:
        HTTPException:
            - 401: If the token is invalid or the employee no longer exists.
    """

    try:
        employee = auth_repo.get_current_employee(token, db)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc

    if not employee:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return employee


@router.post("/register")
def register_employee_auth(
    data: EmployeeAuthCreate,
    db: Session = Depends(get_db),
):
    """
    Register login credentials for an existing employee.

    This endpoint delegates credential creation to the authentication
    repository. Validation includes checking whether the employee exists,
    whether the username is already taken, and whether the employee
    already has login credentials.

    Args:
        data (EmployeeAuthCreate):
            Payload containing employee ID, username, and password.
        db (Session):
            Database session dependency.

    Returns:
        dict: A confirmation message indicating successful creation.

    Raises:
        HTTPException:
            - 400: If validation fails (e.g., username taken, employee not found).
    """

    try:
        auth_repo.register_employee_auth(db, data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {"message": "Login credentials created successfully"}
