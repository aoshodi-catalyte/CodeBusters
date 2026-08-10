import re
from pydantic import BaseModel, field_validator


PHONE_DIGITS_PATTERN = re.compile(r"^\d{10}$")
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class VendorBase(BaseModel):
    active: bool
    name: str
    contact_name: str
    contact_role: str
    email: str
    phone: str 

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        if not EMAIL_PATTERN.match(value):
            raise ValueError("email must be a valid email address")
        return value

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        digits_only = re.sub(r"\D", "", value)
        if not PHONE_DIGITS_PATTERN.match(digits_only):
            raise ValueError("phone number must contain exactly 10 digits")
        return digits_only
