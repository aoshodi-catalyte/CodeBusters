from decimal import Decimal
from pydantic import BaseModel, Field, field_validator
from constants.INGREDIENT_TYPES import UnitOfMeasure, CafeAllergen

# ==========================================
# PYDANTIC SCHEMAS
# ==========================================
class Allergen(BaseModel):
    name: str = Field(min_length=1)

class Ingredient(BaseModel):
    
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
        return UnitOfMeasure.from_string(value)

    @field_validator("allergens", mode="before")
    @classmethod
    def validate_allergens(cls, value):
        if not isinstance(value, list):
            value = [value]
        return [CafeAllergen.from_string(allergen) for allergen in value]

 
