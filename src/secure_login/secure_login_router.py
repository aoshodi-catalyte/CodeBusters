from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from passlib.context import CryptContext  # pyright: ignore[reportMissingImports]
from jose import JWTError, jwt  # type: ignore

from src.database import get_db
from src.employee.employee_model import Employee

router = APIRouter(prefix="/auth", tags=["auth"])


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str):
    return pwd_context.verify(plain, hashed)


# openssl rand -hex 32
SECRET_KEY = "5e48c8f717127b79ef80d3b865a0851091b2761c17895db2776c94081dfa1673"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    employee = db.query(Employee).filter(Employee.email == form_data.username).first()

    if not employee or not verify_password(form_data.password, employee.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    token = create_access_token({"employee_id": employee.id, "role": employee.role})

    return {"access_token": token, "token_type": "bearer"}


def get_current_employee(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        employee_id: int = payload.get("employee_id")
        role: str = payload.get("role")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=401, detail="Employee no longer exists")

    return employee
