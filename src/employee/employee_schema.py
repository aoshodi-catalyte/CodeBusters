from sqlalchemy import Boolean, Column, Date, Float, ForeignKey, Integer, String
# from sqlalchemy.orm import relationship

from database import Base


class EmployeeSchema(Base):
    __tablename__ = "employee"

    id = Column(Integer, primary_key=True, index=True)
    active = Column(Boolean, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)

    role = Column(String, nullable=False)

    hourly_rate = Column(Float, index=True)
    hire_date = Column(Date, index=True)
    term_date = Column(Date, index=True)

    # role = relationship(
    #     "EmployeeRoleSchema",
    #     back_populates="employees"
    # )