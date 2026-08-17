"""
Pydantic models for Customer API data.

This module defines the request and response models used by the Customer API.
CustomerCreate validates and normalizes incoming customer data, while
CustomerResponse formats customer data for API responses.
"""

import re

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    ConfigDict,
    field_validator,
    field_serializer,
)


class CustomerCreate(BaseModel):
    """
    Pydantic model used to validate data when creating a customer.

    Phone numbers are normalized to a 10-digit value before being persisted.
    Names and email addresses are also normalized by removing unnecessary
    surrounding whitespace.
    """

    # Indicates whether the customer is currently active.
    active: bool = True

    # Required first name with a maximum length of 50 characters.
    first_name: str = Field(
        min_length=1,
        max_length=50
    )

    # Optional last name with a maximum length of 50 characters.
    last_name: str | None = Field(
        default=None,
        max_length=50
    )

    # Must be provided and must follow a valid email format.
    email: EmailStr

    # Phone number can be provided with common formatting.
    # It will be normalized to 10 digits before being stored.
    phone_number: str

    # New customers start with zero loyalty points by default.
    loyalty_points: int = Field(
        default=0,
        ge=0
    )

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_names(cls, value: str | None) -> str | None:
        """
        Strip surrounding whitespace from names and reject blank values.

        Args:
            value: Name supplied by the client.

        Returns:
            The normalized name.

        Raises:
            ValueError: If the name contains only whitespace.
        """
        if value is None:
            return None

        value = value.strip()

        if not value:
            raise ValueError("Name must not be blank.")

        return value

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value):
        """
        Normalize surrounding whitespace and capitalization in email addresses.

        EmailStr performs the actual email format validation afterward.
        """
        if isinstance(value, str):
            return value.strip().lower()

        return value

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, value: str) -> str:
        """
        Validate and normalize a phone number.

        Common formatting characters such as hyphens, spaces, parentheses,
        periods, and plus signs are accepted. The resulting value must
        contain exactly 10 digits.

        Args:
            value: Phone number provided by the client.

        Returns:
            The normalized 10-digit phone number.

        Raises:
            ValueError: If the phone number contains invalid characters or
                does not contain exactly 10 digits.
        """
        value = value.strip()

        # Only allow digits and common phone-number formatting characters.
        if not re.fullmatch(r"[\d\s().+-]+", value):
            raise ValueError("Phone number contains invalid characters.")

        digits = re.sub(r"\D", "", value)

        if len(digits) != 10:
            raise ValueError(
                "Phone number must contain exactly 10 digits."
            )

        return digits


class CustomerResponse(BaseModel):
    """
    Pydantic model used to serialize customer data in API responses.

    Phone numbers are stored as 10 digits in the database but are formatted
    as xxx-xxx-xxxx when returned to the client.
    """

    model_config = ConfigDict(from_attributes=True)

    # Database-generated customer ID.
    id: int

    # Indicates whether the customer is currently active.
    active: bool

    # Customer first name.
    first_name: str

    # Customer last name, if provided.
    last_name: str | None

    # Customer email address.
    email: EmailStr

    # Customer phone number.
    phone_number: str

    # Customer loyalty points.
    loyalty_points: int

    @field_serializer("phone_number")
    def format_phone_number(self, value: str) -> str:
        """
        Format a stored 10-digit phone number for API responses.

        Args:
            value: The 10-digit phone number stored in the database.

        Returns:
            Phone number formatted as xxx-xxx-xxxx.
        """
        return (
            f"{value[:3]}-"
            f"{value[3:6]}-"
            f"{value[6:]}"
        )