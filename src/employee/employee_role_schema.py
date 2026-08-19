from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database import Base


class EmployeeRoleSchema(Base):
    """
    Defines the set of valid employee roles used throughout the application.

    Relationships:
        - employees: One-to-Many relationship with EmployeeSchema.
    """

    __tablename__ = "employee_role"

    id = Column(Integer, primary_key=True, index=True)
    role = Column(String, unique=True, nullable=False)
    employees = relationship("EmployeeSchema", back_populates="role")
