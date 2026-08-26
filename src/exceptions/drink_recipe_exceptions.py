class DrinkRecipeError(Exception):
    """Base class for all drink recipe domain errors."""
    pass


class DrinkTypeNotFoundError(DrinkRecipeError):
    """Raised when a drink type enum cannot be mapped to a DB record."""
    def __init__(self, drink_type: str):
        super().__init__(f"Drink type '{drink_type}' not found")


class DuplicateDrinkRecipeNameError(DrinkRecipeError):
    """Raised when a drink recipe name already exists (case-insensitive)."""
    def __init__(self, name: str):
        super().__init__(f"Drink recipe name '{name}' already exists")


class IngredientNotFoundError(DrinkRecipeError):
    """Raised when an ingredient ID does not exist in the database."""
    def __init__(self, ingredient_id: int):
        super().__init__(f"Ingredient ID {ingredient_id} not found")


class UnitConversionError(DrinkRecipeError):
    """Raised when unit conversion fails for an ingredient."""
    def __init__(self, ingredient_name: str, message: str):
        super().__init__(f"Unit conversion failed for ingredient '{ingredient_name}': {message}")
