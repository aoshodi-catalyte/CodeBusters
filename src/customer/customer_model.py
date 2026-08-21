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
    field_serializer
)


# Email validation pattern.
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class CustomerCreate(BaseModel):
    """
    Pydantic model used to validate data when creating a customer.

    Phone numbers are normalized to a 10-digit value before being
    persisted to the database.
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
        min_length=1,
        max_length=50
    )

    # Must be provided and follow the required email pattern.
    # Email addresses are normalized to lowercase.
    email: EmailStr

    # Phone number can be provided with formatting.
    # It will be normalized to 10 digits before being stored.
    phone_number: str

    # New customers start with zero loyalty points.
    # Loyalty points cannot be negative.
    loyalty_points: int = Field(
        default=0,
        ge=0
    )

    @field_validator("email")
    @classmethod
    def validate_and_normalize_email(
        cls,
        value: EmailStr
    ) -> str:
        """
        Validate and normalize the customer's email address.

        The email must match EMAIL_PATTERN and is converted
        to lowercase before being persisted.

        Args:
            value: Email address provided by the client.

        Returns:
            A lowercase, validated email address.

        Raises:
            ValueError: If the email does not match the required pattern.
        """

        email = str(value)

        if not EMAIL_PATTERN.fullmatch(email):
            raise ValueError(
                "Invalid email format."
            )

        return email.lower()

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(
        cls,
        value: str
    ) -> str:
        """
        Validate and normalize a phone number.

        Formatting characters such as hyphens, spaces, and parentheses
        are removed before validation. The resulting value must contain
        exactly 10 digits.

        Args:
            value: Phone number provided by the client.

        Returns:
            The normalized 10-digit phone number.

        Raises:
            ValueError: If the phone number does not contain exactly
                10 digits.
        """

        digits = re.sub(r"\D", "", value)

        if len(digits) != 10:
            raise ValueError(
                "Phone number must contain exactly 10 digits."
            )

        return digits


class CustomerResponse(BaseModel):
    """
    Pydantic model used to serialize customer data in API responses.

    Phone numbers are stored as 10 digits in the database but are
    formatted as xxx-xxx-xxxx when returned to the client.
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

    @field_serializer("email")
    def format_email(
        self,
        value: EmailStr
    ) -> str:
        """
        Ensure email addresses are returned in lowercase.
        """

        return str(value).lower()

    @field_serializer("phone_number")
    def format_phone_number(
        self,
        value: str
    ) -> str:
        """
        Format a stored 10-digit phone number for API responses.

        Returns:
            Phone number formatted as xxx-xxx-xxxx.
        """

        return (
            f"{value[:3]}-"
            f"{value[3:6]}-"
            f"{value[6:]}"
        )
