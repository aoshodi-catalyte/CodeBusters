import re
from pydantic import BaseModel, Field, condecimal, field_validator, model_validator
from constants.EMPLOYEE_ROLES import EmployeeRole
from datetime import date, datetime

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

ConstrainedMoney = condecimal(gt=0, decimal_places=2)
class Employee(BaseModel):
    active: bool
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    email: str
    role: EmployeeRole
    hourly_rate: ConstrainedMoney # type: ignore 
    hire_date: date
    term_date: date | None = None

    
    @field_validator("first_name", "last_name", "email")
    @classmethod
    def validate_not_blank(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("Must not be blank")

        return value

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        """Validate that the email field contains a properly formatted email address.
    
        Uses a regular expression to ensure the email contains one '@' symbol,
        no whitespace, and a valid domain structure.
    
        Args:
            value (str): The email address provided by the user or client.
    
        Returns:
            str: The validated email address.
    
        Raises:
            ValueError: If the email does not match the required pattern.
        """
        if not EMAIL_PATTERN.match(value):
            raise ValueError("email must be a valid email address")
        return value

    @field_validator("role")
    @classmethod
    def validate_role(cls, role_name: str) -> EmployeeRole:
        try:
            return EmployeeRole(role_name)
        except ValueError:
            raise ValueError(f"Invalid role: {role_name}. Valid roles are: {[rn.value for rn in EmployeeRole]}")
        
        
    @field_validator("hire_date", "term_date", mode="before")
    @classmethod
    def validate_date(cls, value):
        if value is None:
            return None

        try:
            return datetime.strptime(value, "%m/%d/%Y").date()
        except ValueError:
            raise ValueError("Date must be in MM/DD/YYYY format")
        
    @model_validator(mode="after")
    def check_term_date_required(self):
        if not self.active and self.term_date is None:
            raise ValueError("Inactive employees must have a term_date.")
        return self