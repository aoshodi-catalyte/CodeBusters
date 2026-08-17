import re
from pydantic import BaseModel, field_validator, Field


PHONE_DIGITS_PATTERN = re.compile(r"^\d{10}$")
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class VendorBase(BaseModel):
    active: bool
    name: str = Field(min_length=1)
    contact_name: str = Field(min_length=1)
    contact_role: str = Field(min_length=1)
    email: str 
    phone: str = Field(min_length=10)


    @field_validator("name", "contact_name", "contact_role", "email", "phone", mode="before")
    @classmethod
    def strip_and_validate_no_trailing_spaces(cls, value: str) -> str:
        """Ensure that string fields do not contain leading or trailing whitespace.

        This validator runs before all other field validators and enforces strict
        whitespace rules across multiple string fields.

        Args:
            value (str): The raw string value provided by the client before any
                normalization or validation occurs.

        Returns:
            str: The cleaned string value with whitespace normalized, provided
                it originally contained no leading or trailing spaces.

        Raises:
            ValueError: If the input contains leading or trailing whitespace,
                such as " bob", "bob ", or any other non‑exact match.
        """
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

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        """Validate that the phone field contains exactly 10 digits.

        All non-digit characters are stripped before validation, allowing
        formatted inputs such as '(555) 123-4567'. After cleaning, the value
        must contain exactly 10 digits.

        Args:
            value (str): The phone number provided by the user or client.

        Returns:
            str: A digits-only phone number string containing exactly 10 digits.

        Raises:
            ValueError: If the cleaned phone number does not contain exactly 10 digits.
        """
        digits_only = re.sub(r"\D", "", value)
        if not PHONE_DIGITS_PATTERN.match(digits_only):
            raise ValueError("phone number must contain exactly 10 digits")
        return digits_only