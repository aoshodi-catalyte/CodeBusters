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
    purchasing_cost: float
    unit_amount: float
    unit_of_measure: str
    allergens: list[AllergenOut]
    vendor_id: int

    model_config = ConfigDict(from_attributes=True)

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
    purchasing_cost: float = Field( ge=0, )
    unit_amount: float = Field( gt=0, )
    unit_of_measure: UnitOfMeasure
    allergens: list[str] = Field(default_factory=list)
    vendor_id: int = Field( gt=0,)

    @field_validator("allergens", mode="before")
    @classmethod
    def validate_allergens(cls, value):
        """
        Convert supplied allergen values into CafeAllergen values.
        A single allergen value is converted into a list so that
        the API accepts either one allergen or multiple allergens.
        Each allergen is converted using CafeAllergen.from_string().
        Args:
            value: A single allergen or list of allergens supplied
                by the client.
        Returns:
            A list of validated CafeAllergen values.

        Raises:
            ValueError: If an allergen cannot be converted into a
                valid CafeAllergen value.
        """    
        if value is None:
            return []
        if not isinstance(value, list):
            value = [value]
        validated_allergens = []
       
        return [
            allergen
            if isinstance(allergen, CafeAllergen)
            else CafeAllergen.from_string(allergen)
            for allergen in value
        ]

    @field_validator("purchasing_cost", "unit_amount")
    @classmethod
    def validate_two_decimal_places(cls, value: float) -> float:
        """
        Validate that numeric ingredient values contain no more
        than two decimal places.
        This validation is applied to purchasing_cost and
        unit_amount before the values are stored in the database.
        It prevents values such as 4.999 from passing API validation
        and being silently rounded by the database.
        Args:
            value: Numeric value supplied for purchasing_cost or
                unit_amount.
        Returns:
            The validated numeric value.
        Raises:
            ValueError: If the value contains more than two decimal
                places.
        """ 
        if round(value, 2) != value:
            raise ValueError("Value must have no more than 2 decimal places")
        return value

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