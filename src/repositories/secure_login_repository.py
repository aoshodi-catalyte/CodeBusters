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


class AuthRepository:
    """Handles authentication, password hashing, JWT creation, and employee lookup."""

    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)

    def verify_password(self, plain: str, hashed: str) -> bool:
        return pwd_context.verify(plain, hashed)

    def authenticate_user(self, db: Session, username: str, password: str):
        auth = db.query(EmployeeAuth).filter(EmployeeAuth.username == username).first()

        if not auth:
            self.verify_password(password, self.hash_password("dummy"))
            return None

        if not self.verify_password(password, auth.password_hash):
            return None

        return auth

    def create_access_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    def get_current_employee(self, token: str, db: Session):
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
