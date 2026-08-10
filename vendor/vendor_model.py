import re
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, field_serializer
from sqlalchemy import Column, Boolean, String, Integer
from database import Base

PHONE_DIGITS_PATTERN = re.compile(r"^\d{10}$")
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class VendorBase(BaseModel):
    active: bool
    name: str
    contact_name: str
    contact_role: str
    email: str
    phone: str = Field(description="10-digit phone number, stored digits-only")

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
            raise ValueError("phone must contain exactly 10 digits")
        return digits_only


class VendorSchema(VendorBase):
    model_config = ConfigDict(from_attributes=True)
    id: int

    @field_serializer("phone")
    def format_phone(self, value: str) -> str:
        return f"{value[0:3]}-{value[3:6]}-{value[6:10]}"


class Vendor(Base):
    __tablename__ = "vendor"

    id = Column(Integer, primary_key=True, index=True, unique=True)
    active = Column(Boolean, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    contact_name = Column(String, index=True, nullable=False)
    contact_role = Column(String, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, index=True, nullable=False)