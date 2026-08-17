from sqlalchemy import Column, Integer, Enum, String
from sqlalchemy.orm import relationship
from database import Base
from constants.EMPLOYEE_ROLES import EmployeeRole

class EmployeeRoleSchema(Base):
    __tablename__ = "employee_role"

    id = Column(Integer, primary_key=True, index=True)
    role = Column(EmployeeRole, unique=True, nullable=False)
    # role = Column(String, unique=True, nullable=False)
    employees = relationship("EmployeeSchema", back_populates="role")