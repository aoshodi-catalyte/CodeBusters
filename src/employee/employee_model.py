from pydantic import BaseModel, Field, condecimal, field_validator
from constants.EMPLOYEE_ROLES import EmployeeRole
from datetime import date

ConstrainedMoney = condecimal(gt=0, decimal_places=2)
class Employee(BaseModel):
    active: bool
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    role: EmployeeRole
    hourly_rate: ConstrainedMoney # type: ignore
    hire_date: date
    term_date: date | None

    @field_validator("role", mode="before")
    def validate_role(cls, value):
        try:
            return EmployeeRole(value)
        except ValueError:
            raise ValueError(f"Invalid role: {value}. Valid roles are: {[r.value for r in EmployeeRole]}")