from pydantic import BaseModel, field_validator


class EmployeeResponse(BaseModel):
    id: int
    active: bool
    first_name: str
    last_name: str
    email: str
    role: str

    @field_validator("role", mode="before")
    @classmethod
    def extract_role_name(cls, value):
        # If given the EmployeeRoleSchema relationship object, pull out the string.
        if hasattr(value, "role"):
            return value.role
        return value
