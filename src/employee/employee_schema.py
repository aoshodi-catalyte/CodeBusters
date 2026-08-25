"""
SQLAlchemy ORM model representing the employee table and its relationship
to employee roles.
"""

from sqlalchemy import Boolean, Column, Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from secure_login.secure_login_schema import EmployeeAuth

from database import Base


class EmployeeSchema(Base):
    """
    Represents an employee record within the system.

    Relationships:
        - role: Many-to-One relationship with EmployeeRoleSchema.
    """

    __tablename__ = "employee"

    id = Column(Integer, primary_key=True, index=True)
    active = Column(Boolean, index=True, nullable=False)
    first_name = Column(String, index=True, nullable=False)
    last_name = Column(String, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)

    role_id = Column(Integer, ForeignKey("employee_role.id"), nullable=False)

    hourly_rate = Column(Float, index=True, nullable=False)
    hire_date = Column(Date, index=True, nullable=False)
    term_date = Column(Date, index=True, nullable=True)

    role = relationship("EmployeeRoleSchema", back_populates="employees")
    auth = relationship("EmployeeAuth", back_populates="employee", uselist=False)
