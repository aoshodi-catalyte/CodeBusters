"""
SQLAlchemy ORM model representing the employee table and its relationship
to employee roles.
"""

from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

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

    # Hourly rate is a monetary value and therefore uses fixed-point
    # decimal precision instead of floating-point storage.
    hourly_rate = Column(Numeric(10, 2), index=True, nullable=False)

    hire_date = Column(Date, index=True, nullable=False)
    term_date = Column(Date, index=True, nullable=True)

    role = relationship("EmployeeRoleSchema", back_populates="employees")
    auth = relationship("EmployeeAuth", back_populates="employee", uselist=False)
