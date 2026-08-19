from pydantic import BaseModel, ConfigDict, field_validator


class EmployeeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    active: bool
    first_name: str
    last_name: str
    email: str
    role: str

    @field_validator("role", mode="before")
    @classmethod
    def extract_role_name(cls, value):
        """
        Extract the role name from nested objects before validation.

        This validator allows the `role` field to accept either:
            - a plain string (e.g., "manager")
            - an object containing a `role` attribute (e.g., ORM model instance)

        If the incoming value has a `role` attribute, the validator returns that
        attribute’s value. Otherwise, the original value is returned unchanged.

        This is useful when API responses are built directly from ORM objects
        where `employee.role` may be an enum, related object, or wrapper.

        Args:
            value (Any): The raw value provided for the `role` field.

        Returns:
            Any: Either the extracted role name or the original value.
        """

        if hasattr(value, "role"):
            return value.role
        return value
