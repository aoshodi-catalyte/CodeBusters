from sqlalchemy import Column, ForeignKey, Integer, String, Enum
from sqlalchemy.orm import relationship

from src.database import Base

class EmployeeSchema(Base):
    __tablename__ = "employee"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    role = Column(Enum(Integer), ForeignKey("employee_role.id"), nullable=False)

    # Relationship with the EmployeeRoleSchema
    role_relationship = relationship("EmployeeRoleSchema", back_populates="employees")