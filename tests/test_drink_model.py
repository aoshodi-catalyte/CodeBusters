from ingredient.ingredient_model import Ingredient
from constants.DRINK_TYPES import DrinkType
from pydantic import ValidationError
from decimal import Decimal
from drink_recipe.drink_recipe_model import DrinkRecipe


def test_valid_drink_recipe():
    ingredient = Ingredient(
        name="Sugar",
        purchasing_cost=Decimal("0.50"),
        unit_amount=Decimal("10.00"),
        unit_of_measure="g",
        allergens=[]
    )

    recipe = DrinkRecipe(
        name="Sweet Coffee",
        description="A sugary coffee drink",
        ingredients=[ingredient],
        active=True,
        type="coffee",
        production_cost=2.50,
        markup_percentage=20,
        sale_price=3.00,
    )

    assert recipe.name == "Sweet Coffee"
    assert recipe.type == DrinkType.COFFEE
    assert len(recipe.ingredients) == 1
    assert recipe.ingredients[0].name == "Sugar"


def test_invalid_drink_type():
    try:
        DrinkRecipe(
            name="Mystery Drink",
            description="Unknown type",
            ingredients=[],
            active=True,
            type="invalid_type",
            production_cost=1.00,
            markup_percentage=10,
            sale_price=1.50,
        )
        assert False
    except ValidationError as exc:
        assert "Input should be 'coffee', 'tea' or 'other'" in str(exc)


def test_negative_production_cost():
    try:
        DrinkRecipe(
            name="Bad Drink",
            description="Negative cost",
            ingredients=[],
            active=True,
            type="tea",
            production_cost=-1.00,
            markup_percentage=10,
            sale_price=2.00,
        )
        assert False
    except ValidationError:
        assert True


def test_negative_markup_percentage():
    try:
        DrinkRecipe(
            name="Bad Drink",
            description="Negative markup",
            ingredients=[],
            active=True,
            type="tea",
            production_cost=1.00,
            markup_percentage=-5,
            sale_price=2.00,
        )
        assert False
    except ValidationError:
        assert True


def test_negative_sale_price():
    try:
        DrinkRecipe(
            name="Bad Drink",
            description="Negative sale price",
            ingredients=[],
            active=True,
            type="tea",
            production_cost=1.00,
            markup_percentage=10,
            sale_price=-2.00,
        )
        assert False
    except ValidationError:
        assert True


def test_default_empty_ingredients():
    recipe = DrinkRecipe(
        name="Plain Tea",
        description="No ingredients",
        active=True,
        type="tea",
        production_cost=0.50,
        markup_percentage=10,
        sale_price=1.00,
    )

    assert recipe.ingredients == []


def test_multiple_ingredients():
    ingredient1 = Ingredient(
        name="Milk",
        purchasing_cost=Decimal("0.30"),
        unit_amount=Decimal("50.00"),
        unit_of_measure="ml",
        allergens=["dairy"]
    )

    ingredient2 = Ingredient(
        name="Honey",
        purchasing_cost=Decimal("0.20"),
        unit_amount=Decimal("10.00"),
        unit_of_measure="g",
        allergens=[]
    )

    recipe = DrinkRecipe(
        name="Honey Milk Tea",
        description="Tea with milk and honey",
        ingredients=[ingredient1, ingredient2],
        active=True,
        type="tea",
        production_cost=1.20,
        markup_percentage=15,
        sale_price=2.00,
    )

    assert len(recipe.ingredients) == 2
    assert recipe.ingredients[0].name == "Milk"
    assert recipe.ingredients[1].name == "Honey"