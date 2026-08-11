from decimal import Decimal
from pydantic import BaseModel, Field


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
    unit_of_measure: str = Field( min_length=1, max_length=50,)
    allergens: list[str] = Field( default_factory=list,) 