"""
Domain-specific exceptions for the drink recipe subsystem.

This module defines a structured hierarchy of custom exceptions used by the
DrinkRecipeRepository to signal business-rule violations and domain errors.
These exceptions allow the repository layer to communicate precise failure
conditions without relying on generic ValueError or database-level errors.

The router layer catches these exceptions and translates them into appropriate
HTTP responses, ensuring a clean separation between domain logic, persistence,
and API concerns.

Exception Overview:
    • DrinkRecipeError
        Base class for all drink recipe domain errors.

    • DrinkTypeNotFoundError
        Raised when a DrinkType enum value cannot be mapped to a corresponding
        database record in the drink_type table.

    • DuplicateDrinkRecipeNameError
        Raised when attempting to create a drink recipe whose normalized name
        already exists in the database.

    • IngredientNotFoundError
        Raised when a recipe references an ingredient ID that does not exist.

    • UnitConversionError
        Raised when unit conversion fails while calculating ingredient usage
        amounts for cost computation.

These exceptions are intentionally narrow and descriptive, enabling clearer
error handling, better test coverage, and more meaningful API responses.
"""

class DrinkRecipeError(Exception):
    """Base class for all drink recipe domain errors."""


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

class DrinkRecipeNotFoundError(DrinkRecipeError):
    """Raised when a drink recipe does not exitst in the DB."""
    def __init__(self, drink_id: int):
        super().__init__(f"Drink Recipe ID {drink_id} not found")