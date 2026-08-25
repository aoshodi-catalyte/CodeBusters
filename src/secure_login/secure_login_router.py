# secure_login_router.py
import os
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from passlib.context import CryptContext  # type: ignore
from jose import JWTError, jwt  # type: ignore

from database import get_db
from employee.employee_schema import EmployeeSchema
from secure_login.secure_login_schema import EmployeeAuth
from secure_login.secure_login_model import EmployeeAuthCreate
from config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str):
    return pwd_context.verify(plain, hashed)


SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def authenticate_user(db: Session, username: str, password: str):
    auth = db.query(EmployeeAuth).filter(EmployeeAuth.username == username).first()

    if not auth:
        verify_password(password, hash_password("dummy"))
        return None

    if not verify_password(password, auth.password_hash):
        return None

    return auth


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    auth = authenticate_user(db, form_data.username, form_data.password)

    if not auth:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    employee = (
        db.query(EmployeeSchema).filter(EmployeeSchema.id == auth.employee_id).first()
    )

    token = create_access_token(
        {"employee_id": employee.id, "role": employee.role.role}
    )

    return {"access_token": token, "token_type": "bearer"}


def get_current_employee(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        employee_id: int = payload.get("employee_id")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    employee = db.query(EmployeeSchema).filter(EmployeeSchema.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=401, detail="Employee no longer exists")

    return employee


@router.post("/register")
def register_employee_auth(data: EmployeeAuthCreate, db: Session = Depends(get_db)):
    employee = (
        db.query(EmployeeSchema).filter(EmployeeSchema.id == data.employee_id).first()
    )

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    existing_username = (
        db.query(EmployeeAuth).filter(EmployeeAuth.username == data.username).first()
    )

    if existing_username:
        raise HTTPException(status_code=400, detail="Username already taken")

    existing_auth = (
        db.query(EmployeeAuth)
        .filter(EmployeeAuth.employee_id == data.employee_id)
        .first()
    )

    if existing_auth:
        raise HTTPException(
            status_code=400, detail="Employee already has login credentials"
        )

    hashed_pw = hash_password(data.password)

    auth_record = EmployeeAuth(
        employee_id=data.employee_id,
        role=employee.role.role,
        username=data.username,
        password_hash=hashed_pw,
    )

    db.add(auth_record)
    db.commit()
    db.refresh(auth_record)

    return {
        "message": "Login credentials created successfully",
        "employee_id": auth_record.employee_id,
        "username": auth_record.username,
        "role": auth_record.role,
    }
