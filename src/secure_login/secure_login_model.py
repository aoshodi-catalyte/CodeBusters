from pydantic import BaseModel, Field


class EmployeeAuthCreate(BaseModel):
    employee_id: int
    username: str
    password: str = Field(max_length=72)
