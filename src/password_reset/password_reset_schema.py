"""
SQLAlchemy model for employee password reset requests.
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class PasswordResetToken(Base):
    """
    Represents a password reset request for an employee.

    The actual reset code is never stored in plaintext.
    Only its hash is persisted.
    """

    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employee.id"), nullable=False, index=True)
    token_hash = Column(String, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)
    channel = Column(String,nullable=False)
    employee = relationship("EmployeeSchema",back_populates="password_reset_tokens")
