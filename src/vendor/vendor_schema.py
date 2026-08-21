"""
SQLAlchemy and Pydantic schemas for vendor records, including ORM mapping and
API response serialization helpers.
"""

from sqlalchemy import Column, Boolean, String, Integer
from sqlalchemy.orm import relationship
from pydantic import ConfigDict, field_serializer

from vendor.vendor_model import VendorBase
from database import Base
from baked_good.baked_good_schema import BakedGoodSchema


class VendorSchema(VendorBase):
    """
    Pydantic response schema for vendor records.

    Extends VendorBase with database-generated fields and serialization helpers.
    """

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
    """
    SQLAlchemy ORM model representing a vendor record in the database.

    Defines table structure and relationships to ingredients and baked goods.
    """

    __tablename__ = "vendor"

    id = Column(Integer, primary_key=True, index=True, unique=True)
    active = Column(Boolean, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    contact_name = Column(String, index=True, nullable=False)
    contact_role = Column(String, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, index=True, nullable=False)
    ingredients = relationship("IngredientSchema", back_populates="vendor")
    baked_goods = relationship(BakedGoodSchema, back_populates="vendor")
