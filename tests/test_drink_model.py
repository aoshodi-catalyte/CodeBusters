import pytest
from decimal import Decimal
from pydantic import ValidationError

from drink_recipe.drink_recipe_model import DrinkRecipe
from constants.DRINK_TYPES import DrinkType


def test_valid_drink_recipe():
    recipe = DrinkRecipe(
        name="Sweet Coffee",
        description="A sugary coffee drink",
        ingredients=[1, 2],
        active=True,
        type="coffee",
        production_cost=Decimal("2.50"),
        markup_percentage=20,
        sale_price=Decimal("3.00"),
    )

    assert recipe.name == "Sweet Coffee"
    assert recipe.ingredients == [1, 2]
    assert recipe.production_cost == Decimal("2.50")
    assert recipe.sale_price == Decimal("3.00")
    assert recipe.type == DrinkType.COFFEE


def test_invalid_drink_type():
    with pytest.raises(ValidationError):
        DrinkRecipe(
            name="Bad Drink",
            description="Wrong type",
            ingredients=[],
            active=True,
            type="invalid_type",
            production_cost=Decimal("1.00"),
            markup_percentage=10,
            sale_price=Decimal("2.00"),
        )


def test_negative_production_cost():
    with pytest.raises(ValidationError):
        DrinkRecipe(
            name="Bad Drink",
            description="Negative cost",
            ingredients=[],
            active=True,
            type="tea",
            production_cost=Decimal("-1.00"),
            markup_percentage=10,
            sale_price=Decimal("2.00"),
        )


def test_negative_sale_price():
    with pytest.raises(ValidationError):
        DrinkRecipe(
            name="Bad Drink",
            description="Negative sale price",
            ingredients=[],
            active=True,
            type="tea",
            production_cost=Decimal("1.00"),
            markup_percentage=10,
            sale_price=Decimal("-2.00"),
        )


def test_default_empty_ingredients():
    recipe = DrinkRecipe(
        name="Plain Tea",
        description="No ingredients",
        active=True,
        type="tea",
        production_cost=Decimal("0.50"),
        markup_percentage=10,
        sale_price=Decimal("1.00"),
    )

    assert recipe.ingredients == []


def test_multiple_ingredients():
    recipe = DrinkRecipe(
        name="Honey Milk Tea",
        description="Tea with milk and honey",
        ingredients=[1, 2, 3],
        active=True,
        type="tea",
        production_cost=Decimal("1.20"),
        markup_percentage=15,
        sale_price=Decimal("2.00"),
    )

    assert recipe.ingredients == [1, 2, 3]
