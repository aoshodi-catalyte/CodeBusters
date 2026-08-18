from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database import Base


class EmployeeRoleSchema(Base):
    __tablename__ = "employee_role"

    id = Column(Integer, primary_key=True, index=True)
    role = Column(String, unique=True, nullable=False)
    employees = relationship("EmployeeSchema", back_populates="role")
