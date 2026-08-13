from pydantic import BaseModel, Field, field_validator
from constants.EMPLOYEE_ROLES import EmployeeRole
from datetime import date


class Employee(BaseModel):
    id: int
    active: bool
    first_name: str
    last_name: str
    role: EmployeeRole
    hourly_rate: float
    hire_date: date
    term_date: date | None

    @field_validator('role')
    def validate_role(role: str) -> EmployeeRole:
        try:
            return EmployeeRole(role)
        except ValueError:
            raise ValueError(f"Invalid role: {role}. Valid roles are: {[r.value for r in EmployeeRole]}")