<<<<<<< HEAD
"""
Pydantic schemas for ingredient data validation and API responses.

This module defines request and response models for ingredients, including
allergen handling, unit‑of‑measure validation, decimal precision checks, and
normalization of user‑supplied values. These schemas ensure that ingredient
data entering or leaving the API is fully validated, structured, and ready
for use by repository and service layers.
"""
=======
"""Pydantic schemas for ingredient validation and API responses."""
>>>>>>> 0d25e2769e93a16f5d8d0d058327506f2bc2ee73

from pydantic import BaseModel, ConfigDict, Field, field_validator

from constants.ingredient_types import CafeAllergen, UnitOfMeasure

<<<<<<< HEAD

class AllergenOut(BaseModel):
    """Response schema representing an ingredient allergen."""

=======

class AllergenOut(BaseModel):
    """Schema used when returning an allergen to the client."""

>>>>>>> 0d25e2769e93a16f5d8d0d058327506f2bc2ee73
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
    purchasing_cost: float
    unit_amount: float
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
        name: Name of the ingredient. Must be between 1 and
            255 characters after whitespace is removed.
        purchasing_cost: Cost paid to purchase the ingredient.
            Must be greater than or equal to zero and contain
            no more than two decimal places.
        unit_amount: Quantity represented by the unit of measure.
            Must be greater than zero and contain no more than
            two decimal places.
        unit_of_measure: Unit used to measure the ingredient.
            Must be a valid UnitOfMeasure value.
        allergens: List of allergens associated with the ingredient.
            Each allergen must be a valid CafeAllergen value.
        vendor_id: ID of the vendor supplying the ingredient.
            Must be greater than zero.
    """

    active: bool = True
<<<<<<< HEAD

    name: str = Field(
        min_length=1,
        max_length=255,
    )

    purchasing_cost: float = Field(
        ge=0,
    )

    unit_amount: float = Field(
        gt=0,
    )

    unit_of_measure: UnitOfMeasure

    allergens: list[CafeAllergen] = Field(
        default_factory=list,
    )

    vendor_id: int = Field(
        gt=0,
    )
=======
    name: str = Field(min_length=1, max_length=255)
    purchasing_cost: float = Field(ge=0)
    unit_amount: float = Field(gt=0)
    unit_of_measure: UnitOfMeasure
    allergens: list[str] = Field(default_factory=list)
    vendor_id: int = Field(gt=0)
>>>>>>> 0d25e2769e93a16f5d8d0d058327506f2bc2ee73

    @field_validator("name", mode="before")
    @classmethod
    def strip_name(cls, value: str) -> str:
        """Remove leading and trailing whitespace from the name.

        Args:
            value: Ingredient name supplied by the client.

        Returns:
            Ingredient name with surrounding whitespace removed.

        Raises:
            ValueError: If the value is not a string or is blank after
                whitespace is removed.
        """
        if not isinstance(value, str):
            raise ValueError("Ingredient name must be a string")

        value = value.strip()

        if not value:
            raise ValueError("Ingredient name cannot be blank")

        return value

    @field_validator("allergens", mode="before")
    @classmethod
    def validate_allergens(cls, value) -> list[CafeAllergen]:
        """Convert supplied allergen values into CafeAllergen values.

        A single allergen value is converted into a list so the API
        accepts either one allergen or multiple allergens.

        Args:
            value: Single allergen or list of allergens supplied by
                the client.

        Returns:
            A list of validated CafeAllergen values.

        Raises:
<<<<<<< HEAD
            ValueError: If an allergen is not recognized.
=======
            ValueError: If an allergen cannot be converted into a
                valid CafeAllergen value.
>>>>>>> 0d25e2769e93a16f5d8d0d058327506f2bc2ee73
        """
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

    @field_validator("purchasing_cost", "unit_amount")
    @classmethod
<<<<<<< HEAD
    def validate_two_decimal_places(
        cls,
        value: float,
    ) -> float:
        """Validate that numeric values contain at most two decimals.

        Args:
            value: Numeric ingredient value.
=======
    def validate_two_decimal_places(cls, value: float) -> float:
        """Validate that a numeric value has at most two decimals.

        Args:
            value: Numeric ingredient value supplied by the client.
>>>>>>> 0d25e2769e93a16f5d8d0d058327506f2bc2ee73

        Returns:
            The validated numeric value.

        Raises:
<<<<<<< HEAD
            ValueError: If the value contains more than two decimals.
=======
            ValueError: If the value contains more than two decimal
                places.
>>>>>>> 0d25e2769e93a16f5d8d0d058327506f2bc2ee73
        """
        if round(value, 2) != value:
            raise ValueError(
                "Value must have no more than 2 decimal places"
            )

        return value

    @field_validator("unit_of_measure", mode="before")
    @classmethod
<<<<<<< HEAD
    def validate_unit_of_measure(
        cls,
        value,
    ) -> UnitOfMeasure:
        """Convert the supplied value into a UnitOfMeasure.
=======
    def validate_unit_of_measure(cls, value: str) -> UnitOfMeasure:
        """Convert a supplied string into a UnitOfMeasure value.
>>>>>>> 0d25e2769e93a16f5d8d0d058327506f2bc2ee73

        Args:
            value: Unit of measure supplied by the client.

        Returns:
            A valid UnitOfMeasure enum value.

        Raises:
            ValueError: If the supplied value is not a valid unit.
        """
        return UnitOfMeasure.from_string(value)


class IngredientListResponse(BaseModel):
    """Schema used when returning a list of ingredients.

    Attributes:
        message: Message describing the response.
        ingredients: List of ingredients returned by the API.
    """

    message: str
    ingredients: list[IngredientOut]