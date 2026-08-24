"""
Pydantic response schema for vendor records, including serialization helpers
for formatting phone numbers in API responses.
"""

from pydantic import BaseModel, field_serializer, ConfigDict


class VendorResponse(BaseModel):
    """
    Defines the shape of vendor data returned in API responses.

    Extends the base vendor model with database-generated fields and
    serialization logic for human-readable formatting.
    """

    model_config = ConfigDict(from_attributes=True)

    active: bool
    name: str
    contact_name: str
    contact_role: str
    email: str
    phone: str
    id: int

    @field_serializer("phone")
    def format_phone(self, value: str) -> str:
        """Format the phone number into a standard XXX-XXX-XXXX pattern.

        Converts the digits-only phone number stored in the database into a
        human-readable format for API responses.

        Args:
            value (str): A digits-only phone number string (e.g., "5551234567").

        Returns:
            str: A formatted phone number string (e.g., "555-123-4567").
        """
        return f"{value[0:3]}-{value[3:6]}-{value[6:10]}"