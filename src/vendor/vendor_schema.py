from src.vendor.vendor_model import VendorBase
from sqlalchemy import Column, Boolean, String, Integer
from pydantic import ConfigDict, field_serializer
from database import Base


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