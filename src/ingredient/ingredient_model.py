"""Pydantic schemas for ingredient validation and API responses."""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from constants.ingredient_types import CafeAllergen, UnitOfMeasure


class AllergenOut(BaseModel):
    """Schema used when returning an allergen to the client."""

    name: str

    model_config = ConfigDict(from_attributes=True)


class Allergen(BaseModel):
    """Schema used to validate an ingredient allergen.

    Attributes:
        name: Name of the allergen. Must contain at least one character.
    """

    name: str = Field(min_length=1)


class IngredientOut(BaseModel):
    """Schema used when returning an ingredient to the client.

    Attributes:
        id: Unique identifier for the ingredient.
        name: Ingredient name.
        active: Whether the ingredient is active.
        purchasing_cost: Cost of purchasing the ingredient.
        unit_amount: Quantity represented by the unit of measure.
        unit_of_measure: Unit used to measure the ingredient.
        allergens: Allergens associated with the ingredient.
        vendor_id: ID of the vendor supplying the ingredient.
    """

    id: int
    name: str
    active: bool
    purchasing_cost: Decimal = Field(decimal_places=2)
    unit_amount: Decimal = Field(decimal_places=2)
    unit_of_measure: str
    allergens: list[AllergenOut]
    vendor_id: int

    model_config = ConfigDict(from_attributes=True)


class Ingredient(BaseModel):
    """Schema used to validate ingredient data.

    This schema validates ingredient information before it is
    passed to the repository for database creation or updating.

    Attributes:
        active: Whether the ingredient is currently active.
        name: Ingredient name.
        purchasing_cost: Cost paid to purchase the ingredient.
        unit_amount: Quantity represented by the unit of measure.
        unit_of_measure: Unit used to measure the ingredient.
        allergens: List of allergens associated with the ingredient.
        vendor_id: ID of the vendor supplying the ingredient.
    """

    active: bool = True
    name: str = Field(min_length=1, max_length=255)
    purchasing_cost: Decimal = Field(ge=0, decimal_places=2)
    unit_amount: Decimal = Field(gt=0, decimal_places=2)
    unit_of_measure: UnitOfMeasure
    allergens: list[str] = Field(default_factory=list)
    vendor_id: int = Field(gt=0)

    @field_validator("name", mode="before")
    @classmethod
    def strip_name(cls, value: str) -> str:
        """Remove leading and trailing whitespace from the name."""

        if not isinstance(value, str):
            raise ValueError("Ingredient name must be a string")

        value = value.strip()

        if not value:
            raise ValueError("Ingredient name cannot be blank")

        return value

    @field_validator("allergens", mode="before")
    @classmethod
    def validate_allergens(cls, value) -> list[CafeAllergen]:
        """Convert supplied allergen values into CafeAllergen values."""

        if value is None:
            return []

        if not isinstance(value, list):
            value = [value]

        return [
            allergen
            if isinstance(allergen, CafeAllergen)
            else CafeAllergen.from_string(allergen)
            for allergen in value
        ]

    @field_validator("unit_of_measure", mode="before")
    @classmethod
    def validate_unit_of_measure(cls, value: str) -> UnitOfMeasure:
        """Convert a supplied string into a UnitOfMeasure value."""

        return UnitOfMeasure.from_string(value)
