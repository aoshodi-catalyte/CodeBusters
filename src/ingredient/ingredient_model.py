from decimal import Decimal
from pydantic import BaseModel, Field, field_validator, ConfigDict
from constants.INGREDIENT_TYPES import UnitOfMeasure, CafeAllergen

# ==========================================
# PYDANTIC SCHEMAS
# ==========================================
class AllergenOut(BaseModel):
    name: str

    model_config = ConfigDict(from_attributes=True)

class Allergen(BaseModel):
    """
    Pydantic schema representing an ingredient allergen.

    Attributes:
        name: Name of the allergen. Must contain at least one character.
    """    
    name: str = Field(min_length=1)

class IngredientOut(BaseModel):
    id: int
    name: str
    active: bool
    purchasing_cost: Decimal
    unit_amount: Decimal
    unit_of_measure: str
    allergens: list[AllergenOut]
    vendor_id: int

    model_config = {"from_attributes": True}

class Ingredient(BaseModel):
    
    """
    Pydantic schema used to validate ingredient data.

    This schema validates ingredient information before it is
    passed to the repository for database creation.

    Attributes:
        active: Whether the ingredient is currently active.
            Defaults to True.
        name: Name of the ingredient. Must be between 1 and
            255 characters.
        purchasing_cost: Cost paid to purchase the ingredient.
            Must be greater than or equal to zero and contain
            no more than two decimal places.
        unit_amount: Quantity of the ingredient represented by
            the unit of measure. Must be greater than zero and
            contain no more than two decimal places.
        unit_of_measure: Unit used to measure the ingredient.
            Must be a valid UnitOfMeasure value.
        allergens: List of allergens associated with the ingredient.
            Each allergen must be a valid CafeAllergen value.
        vendor_id: ID of the vendor supplying the ingredient.
            Must be greater than zero.The referenced vendor must
            also exist in the database before the ingredient can
            be created.
    """

    active: bool = True
    name: str = Field(min_length=1, max_length=255)
    purchasing_cost: Decimal = Field( ge=0, decimal_places=2,)
    unit_amount: Decimal = Field( gt=0, decimal_places=2, )
    unit_of_measure: UnitOfMeasure
    allergens: list[CafeAllergen]
    vendor_id: int = Field( gt=0,)

    @field_validator("unit_of_measure", mode="before")
    @classmethod
    def validate_unit_of_measure(cls, value):
        """
        Convert the supplied unit of measure into a UnitOfMeasure.

        The validator runs before Pydantic performs the normal
        field validation, allowing values such as strings to be
        converted using UnitOfMeasure.from_string().

        Args:
            value: The unit of measure supplied by the client.

        Returns:
            A valid UnitOfMeasure value.

        Raises:
            ValueError: If the supplied value cannot be converted
                to a valid UnitOfMeasure.
        """   
        return UnitOfMeasure.from_string(value)

    @field_validator("allergens", mode="before")
    @classmethod
    def validate_allergens(cls, value):
        """
        Convert supplied allergen values into CafeAllergen values.

        A single allergen value is converted into a list so that
        the API accepts either one allergen or multiple allergens.
        Each allergen is then converted using CafeAllergen.from_string().

        Args:
            value: A single allergen or a list of allergens supplied
                by the client.

        Returns:
            A list of valid CafeAllergen values.

        Raises:
            ValueError: If an allergen cannot be converted into a
                valid CafeAllergen.
        """    
        if not isinstance(value, list):
            value = [value]
        return [CafeAllergen.from_string(allergen) for allergen in value]

 
