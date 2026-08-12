from vendor.vendor_model import VendorBase
from database import Base
from sqlalchemy import Column, Boolean, String, Integer
from sqlalchemy.orm import relationship
from pydantic import ConfigDict, field_serializer


class VendorSchema(VendorBase):
    model_config = ConfigDict(from_attributes=True)
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


class Vendor(Base):
    __tablename__ = "vendor"

    id = Column(Integer, primary_key=True, index=True, unique=True)
    active = Column(Boolean, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    contact_name = Column(String, index=True, nullable=False)
    contact_role = Column(String, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, index=True, nullable=False)
    ingredients = relationship("IngredientSchema", back_populates="vendor")
    baked_goods = relationship("BakedGoodSchema", back_populates="vendor")