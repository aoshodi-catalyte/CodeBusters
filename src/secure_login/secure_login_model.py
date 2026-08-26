"""
Pydantic model used when creating new authentication credentials
for an existing employee.

This schema is consumed by the `/auth/register` endpoint and ensures:
- The employee ID is provided
- The username is provided
- The password meets length constraints (bcrypt max 72 chars)
"""

from pydantic import BaseModel, Field


class EmployeeAuthCreate(BaseModel):
    """
    Schema for creating employee authentication credentials.

    Attributes:
        employee_id (int): The ID of the employee receiving login credentials.
        username (str): The desired username for authentication.
        password (str): Plaintext password, limited to 72 characters due to bcrypt constraints.
    """

    employee_id: int
    username: str
    password: str = Field(max_length=72)
