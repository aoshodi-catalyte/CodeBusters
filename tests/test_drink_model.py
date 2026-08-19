import pytest
from pydantic import ValidationError

from drink_recipe.drink_recipe_model import DrinkRecipe
from constants.DRINK_TYPES import DrinkType
from drink_recipe.drink_recipe_model import RecipeIngredient


def test_valid_drink_recipe():
    recipe = DrinkRecipe(
        name="Sweet Coffee",
        description="A sugary coffee drink",
        ingredients=[
            {"id": 1, "quantity_used": 0.50, "unit_of_measure_used": "cup"},
            {"id": 2, "quantity_used": 2.00, "unit_of_measure_used": "tbsp"},
        ],
        active=True,
        type="coffee",
        markup_percentage=20,
    )

    assert recipe.name == "Sweet Coffee"
    assert recipe.ingredients[0] == RecipeIngredient(
        id=1, quantity_used=0.50, unit_of_measure_used="cup"
    )
    assert recipe.ingredients[1] == RecipeIngredient(
        id=2, quantity_used=2.00, unit_of_measure_used="tbsp"
    )
    assert recipe.markup_percentage == 20
    assert recipe.type == DrinkType.COFFEE


def test_invalid_drink_type():
    with pytest.raises(ValidationError):
        DrinkRecipe(
            name="Bad Drink",
            description="Wrong type",
            ingredients=[],
            active=True,
            type="invalid_type",
            markup_percentage=10,
        )


def test_default_empty_ingredients():
    recipe = DrinkRecipe(
        name="Plain Tea",
        description="No ingredients",
        active=True,
        type="tea",
        markup_percentage=10,
    )

    assert recipe.ingredients == []


def test_multiple_ingredients():
    recipe = DrinkRecipe(
        name="Honey Milk Tea",
        description="Tea with milk and honey",
        ingredients=[
            {"id": 1, "quantity_used": 0.50, "unit_of_measure_used": "cup"},
            {"id": 2, "quantity_used": 2.00, "unit_of_measure_used": "tbsp"},
            {"id": 3, "quantity_used": 1.00, "unit_of_measure_used": "tbsp"},
        ],
        active=True,
        type="tea",
        markup_percentage=15,
    )

    assert recipe.ingredients[0] == RecipeIngredient(
        id=1, quantity_used=0.50, unit_of_measure_used="cup"
    )
    assert recipe.ingredients[1] == RecipeIngredient(
        id=2, quantity_used=2.00, unit_of_measure_used="tbsp"
    )
    assert recipe.ingredients[2] == RecipeIngredient(
        id=3, quantity_used=1.00, unit_of_measure_used="tbsp"
    )
