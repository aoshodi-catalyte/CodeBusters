"""Pydantic schemas for ingredient validation and responses."""

from pydantic import BaseModel, ConfigDict, Field, field_validator

from constants.INGREDIENT_TYPES import CafeAllergen, UnitOfMeasure


class AllergenOut(BaseModel):
    """Response schema representing an ingredient allergen."""

    name: str

    model_config = ConfigDict(from_attributes=True)


class Allergen(BaseModel):
    """Schema representing an ingredient allergen.

    Attributes:
        name: Name of the allergen. Must contain at least one character.
    """

    name: str = Field(min_length=1)


class IngredientOut(BaseModel):
    """Response schema representing an ingredient."""

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
    passed to the repository for database creation or update.

    Attributes:
        active: Whether the ingredient is currently active.
        name: Name of the ingredient. Must be between 1 and
            255 characters.
        purchasing_cost: Cost to purchase the ingredient. Must be
            greater than or equal to zero and contain no more than
            two decimal places.
        unit_amount: Quantity represented by the unit of measure.
            Must be greater than zero and contain no more than
            two decimal places.
        unit_of_measure: Unit used to measure the ingredient.
        allergens: List of allergens associated with the ingredient.
        vendor_id: ID of the vendor supplying the ingredient.
            Must be greater than zero.
    """

    active: bool = True

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

    @field_validator("name", mode="before")
    @classmethod
    def strip_name(cls, value: str) -> str:
        """Remove leading and trailing whitespace from the name.

        Args:
            value: Ingredient name supplied by the client.

        Returns:
            The stripped ingredient name.

        Raises:
            ValueError: If the value is not a string or is blank.
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
        """Convert supplied allergens into CafeAllergen values.

        A single allergen value is converted into a list so that
        the API accepts either one allergen or multiple allergens.

        Args:
            value: A single allergen or list of allergens.

        Returns:
            A list of validated CafeAllergen values.

        Raises:
            ValueError: If an allergen is not recognized.
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
    def validate_two_decimal_places(
        cls,
        value: float,
    ) -> float:
        """Validate that numeric values contain at most two decimals.

        Args:
            value: Numeric ingredient value.

        Returns:
            The validated numeric value.

        Raises:
            ValueError: If the value contains more than two decimals.
        """
        if round(value, 2) != value:
            raise ValueError(
                "Value must have no more than 2 decimal places"
            )

        return value

    @field_validator("unit_of_measure", mode="before")
    @classmethod
    def validate_unit_of_measure(
        cls,
        value,
    ) -> UnitOfMeasure:
        """Convert the supplied value into a UnitOfMeasure.

        Args:
            value: Unit of measure supplied by the client.

        Returns:
            A valid UnitOfMeasure value.

        Raises:
            ValueError: If the unit of measure is not recognized.
        """
        return UnitOfMeasure.from_string(value)


class IngredientListResponse(BaseModel):
    """Response schema containing a list of ingredients."""

    message: str
    ingredients: list[IngredientOut]