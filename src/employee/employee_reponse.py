from pydantic import BaseModel

class EmployeeResponse(BaseModel):
    id: int
    active: bool
    first_name: str
    last_name: str
    email: str
    role: str