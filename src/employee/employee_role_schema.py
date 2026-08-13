from sqlalchemy import Column, Integer, Enum, String
from sqlalchemy.orm import relationship
from src.database import Base

class EmployeeRoleSchema(Base):
    __tablename__ = "employee_role"

    id = Column(Integer, primary_key=True, index=True)
    role = Column(Enum(String), unique=True, nullable=False)

    # Relationship with the EmployeeSchema
    employees = relationship("EmployeeSchema", back_populates="role")