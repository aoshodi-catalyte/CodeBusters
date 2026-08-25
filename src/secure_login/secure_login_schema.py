"""
SQLAlchemy ORM model representing authentication credentials for employees.

This table stores:
- Username and hashed password
- The employee the credentials belong to
- The employee's role at the time of credential creation

Each employee may have exactly one authentication record.
"""

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class EmployeeAuth(Base):
    """
    Represents login credentials for an employee.

    Attributes:
        id (int): Primary key for the authentication record.
        employee_id (int): Foreign key referencing the employee this login belongs to.
        role (str): The employee's role at the time of credential creation.
        username (str): Unique username used for login.
        password_hash (str): Bcrypt-hashed password.
        employee (EmployeeSchema): Relationship to the associated employee.
    """

    __tablename__ = "employee_auth"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employee.id"), nullable=False)

    role = Column(String, nullable=False)

    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)

    employee = relationship("EmployeeSchema", back_populates="auth")
