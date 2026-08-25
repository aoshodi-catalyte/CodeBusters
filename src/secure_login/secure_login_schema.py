from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class EmployeeAuth(Base):
    __tablename__ = "employee_auth"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employee.id"), nullable=False)

    role = Column(String, nullable=False)

    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)

    employee = relationship("EmployeeSchema", back_populates="auth")
