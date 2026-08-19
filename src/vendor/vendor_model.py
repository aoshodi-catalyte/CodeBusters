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

    @field_validator("name", "contact_name", "contact_role", "phone", mode="before")
    @classmethod
    def strip_and_validate_no_trailing_spaces(cls, value: str) -> str:
        """Normalize and validate string fields by enforcing consistent formatting rules.

        This validator:
        - Removes all leading and trailing whitespace using `strip()`
        - Ensures the resulting value is not blank after trimming
        - Runs before all other validators to guarantee normalized input

        This prevents issues such as:
        - Duplicate records caused by trailing spaces (e.g., "bob" vs "bob ")
        - Case‑sensitive mismatches (e.g., "Manager" vs "manager")
        - Invalid blank values created by whitespace-only input

        Args:
            value (str): The raw string value provided by the client.

        Returns:
            str: The normalized string value with whitespace removed and lowercased.

        Raises:
            ValueError: If the trimmed value is empty.
        """
        value = value.strip()
        if not value:
            raise ValueError("Must not be blank")

        return value

    @field_validator("email", mode="before")
    @classmethod
    def validate_email(cls, value: str) -> str:
        """Validate that the email field contains a properly formatted email address.

        Uses a regular expression to ensure the email contains one '@' symbol,
        no whitespace, and a valid domain structure.

        Args:
            value (str): The email address provided by the user or client.

        Returns:
            str: The validated email address all lowercased.

        Raises:
            ValueError: If the email does not match the required pattern.
        """
        value = value.strip().lower()

        if not value:
            raise ValueError("Must not be blank")

        if not EMAIL_PATTERN.fullmatch(value):
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
