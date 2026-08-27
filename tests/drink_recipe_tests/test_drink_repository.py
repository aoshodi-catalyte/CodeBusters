import pytest

from constants.drink_types import DrinkType
from drink_recipe.drink_type_schema import DrinkTypeSchema
from exceptions.drink_recipe_exceptions import (
    DrinkRecipeNotFoundError,
    DrinkTypeNotFoundError,
    DuplicateDrinkRecipeNameError,
    IngredientNotFoundError,
    UnitConversionError,
)
from ingredient.ingredient_schema import IngredientSchema
from repositories.drink_recipe_repository import DrinkRecipeRepository, map_enum_to_fk
from tests.factories.drink_recipe_factories import (
    drink_types,
    ingredient_factory,
    recipe_model_factory,
)


@pytest.fixture
def repo(db):
    return DrinkRecipeRepository(db)


def test_map_enum_to_fk_success(db, drink_types):
    fk_id = map_enum_to_fk(DrinkType.COFFEE, db)
    assert fk_id == drink_types["coffee"].id


def test_map_enum_to_fk_missing_type(db):
    with pytest.raises(DrinkTypeNotFoundError):
        map_enum_to_fk(DrinkType.TEA, db)


def test_create_drink_recipe(repo, db, drink_types, ingredient_factory, recipe_model_factory):
    milk = ingredient_factory(name="Milk", cost=4.00, amount=1.00, uom="gal")
    espresso = ingredient_factory(name="Espresso Beans", cost=14.00, amount=1.00, uom="lb")
    sugar = ingredient_factory(name="Sugar", cost=2.50, amount=4.00, uom="lb")

    recipe = recipe_model_factory(
        name="20oz Latte",
        description="Milk, espresso, sugar",
        ingredients=[
            (milk, 16.00, "fl_oz"),
            (espresso, 4.00, "oz"),
            (sugar, 8.40, "g"),
        ],
        drink_type="coffee",
        markup=81,
    )

    created = repo.create_drink_recipe(recipe)

    assert created.production_cost == pytest.approx(4.01, rel=1e-2)
    assert created.sale_price == pytest.approx(7.26, rel=1e-2)
    assert len(created.recipe_ingredients) == 3


def test_duplicate_drink_recipe_name(repo, db, drink_types, recipe_model_factory):
    recipe = recipe_model_factory(
        name="Latte",
        description="desc",
        ingredients=[],
        drink_type="coffee",
        markup=10,
    )

    repo.create_drink_recipe(recipe)

    recipe1 = recipe_model_factory(
        name="Latte",
        description="desc",
        ingredients=[],
        drink_type="coffee",
        markup=10,
    )

    with pytest.raises(DuplicateDrinkRecipeNameError):
        repo.create_drink_recipe(recipe1)


def test_missing_ingredient(repo, db, drink_types, recipe_model_factory):
    recipe = recipe_model_factory(
        name="Bad Latte",
        description="desc",
        ingredients=[(IngredientSchema(id=999), 1.0, "g")],
        drink_type="coffee",
        markup=10,
    )

    with pytest.raises(IngredientNotFoundError):
        repo.create_drink_recipe(recipe)


def test_unit_conversion_failure(repo, db, drink_types, ingredient_factory, recipe_model_factory):
    ing = ingredient_factory(name="Milk", cost=4.00, amount=1.00, uom="gal")

    recipe = recipe_model_factory(
        name="Broken Latte",
        description="desc",
        ingredients=[(ing, 1.0, "banana")],
        drink_type="coffee",
        markup=10,
    )

    with pytest.raises(UnitConversionError):
        repo.create_drink_recipe(recipe)


def test_get_all_drink_recipes(repo, db, drink_types, ingredient_factory, recipe_model_factory):
    milk = ingredient_factory(name="Milk", cost=4.00, amount=1.00, uom="gal")
    espresso = ingredient_factory(name="Espresso Beans", cost=14.00, amount=1.00, uom="lb")
    sugar = ingredient_factory(name="Sugar", cost=2.50, amount=4.00, uom="lb")

    recipe = recipe_model_factory(
        name="20oz Latte",
        description="Milk, espresso, sugar",
        ingredients=[
            (milk, 16.00, "fl_oz"),
            (espresso, 4.00, "oz"),
            (sugar, 8.40, "g"),
        ],
        drink_type="coffee",
        markup=81,
    )

    repo.create_drink_recipe(recipe)

    recipe = recipe_model_factory(
        name="20oz Matcha Latte",
        description="Milk, matcha, sugar",
        ingredients=[
            (milk, 16.00, "fl_oz"),
            (sugar, 8.40, "g"),
        ],
        drink_type="tea",
        markup=81,
    )

    repo.create_drink_recipe(recipe)

    all_recipes = repo.get_all_drink_recipes()

    assert len(all_recipes) == 2
    assert all_recipes[0].name == "20oz Latte"
    assert all_recipes[1].name == "20oz Matcha Latte"

def test_get_all_drink_recipes_empty(repo):
    all_recipees = repo.get_all_drink_recipes()

    assert len(all_recipees) == 0


def test_get_by_id(repo, db, drink_types, ingredient_factory, recipe_model_factory):
    milk = ingredient_factory(name="Milk", cost=4.00, amount=1.00, uom="gal")
    espresso = ingredient_factory(name="Espresso Beans", cost=14.00, amount=1.00, uom="lb")
    sugar = ingredient_factory(name="Sugar", cost=2.50, amount=4.00, uom="lb")

    recipe = recipe_model_factory(
        name="20oz Latte",
        description="Milk, espresso, sugar",
        ingredients=[
            (milk, 16.00, "fl_oz"),
            (espresso, 4.00, "oz"),
            (sugar, 8.40, "g"),
        ],
        drink_type="coffee",
        markup=81,
    )

    created = repo.create_drink_recipe(recipe)
    drink = repo.get_drink_recipe_by_id(created.id)

    assert drink.production_cost == pytest.approx(4.01, rel=1e-2)
    assert drink.sale_price == pytest.approx(7.26, rel=1e-2)
    assert len(drink.recipe_ingredients) == 3


def test_get_by_id_not_found(repo):
    with pytest.raises(DrinkRecipeNotFoundError):
        repo.get_drink_recipe_by_id(999)


def test_update_drink_recipe_success(repo, db, drink_types, ingredient_factory, recipe_model_factory):
    ing = ingredient_factory(name="Milk", cost=8.00, amount=1.00, uom="gal")

    recipe = recipe_model_factory(
        name="5 oz Latte",
        description="desc",
        ingredients=[(ing, 5.0, "fl_oz")],
        drink_type="coffee",
        markup=10,
    )

    created = repo.create_drink_recipe(recipe)

    payload = recipe_model_factory(
        name="10 oz Latte",
        description="desc",
        ingredients=[(ing, 10.00, "fl_oz")],
        drink_type="coffee",
        markup=20,
    )

    updated = repo.update_drink_recipe_by_id(created.id, payload)

    print(updated)

    assert updated.name == "10 oz Latte"
    assert len(updated.recipe_ingredients) == 1

    ri = updated.recipe_ingredients[0]
    assert ri.ingredient_id == ing.id
    assert float(ri.quantity_used) == 10.00
    assert ri.unit_of_measure_used == "fl_oz"


def test_update_drink_recipe_not_found(repo, db, recipe_model_factory):
    recipe = recipe_model_factory(
        name="Latte",
        description="desc",
        ingredients=[],
        drink_type="coffee",
        markup=10,
    )

    with pytest.raises(DrinkRecipeNotFoundError):
        repo.update_drink_recipe_by_id(999, recipe)


def test_update_drink_recipe_ingredient_not_found(repo, db, drink_types, ingredient_factory, recipe_model_factory):
    ing = ingredient_factory(name="Milk", cost=4.00, amount=1.00, uom="gal")

    recipe = recipe_model_factory(
        name="Latte",
        description="desc",
        ingredients=[(ing, 5.0, "fl_oz")],
        drink_type="coffee",
        markup=10,
    )

    created = repo.create_drink_recipe(recipe)

    bad_payload = recipe_model_factory(
        name="Latte",
        description="desc",
        ingredients=[(IngredientSchema(id=999), 1.0, "cup")],
        drink_type="coffee",
        markup=10,
    )

    with pytest.raises(IngredientNotFoundError):
        repo.update_drink_recipe_by_id(created.id, bad_payload)


def test_update_drink_recipe_drink_type_not_found(repo, db, drink_types, ingredient_factory, recipe_model_factory):
    ing = ingredient_factory(name="Milk", cost=4.00, amount=1.00, uom="gal")

    recipe = recipe_model_factory(
        name="Latte",
        description="desc",
        ingredients=[(ing, 5.0, "fl_oz")],
        drink_type="coffee",
        markup=10,
    )

    created = repo.create_drink_recipe(recipe)

    # Remove drink types
    db.query(DrinkTypeSchema).delete()
    db.commit()

    bad_payload = recipe_model_factory(
        name="Latte",
        description="desc",
        ingredients=[(ing, 1.0, "cup")],
        drink_type="coffee",
        markup=10,
    )

    with pytest.raises(DrinkTypeNotFoundError):
        repo.update_drink_recipe_by_id(created.id, bad_payload)
