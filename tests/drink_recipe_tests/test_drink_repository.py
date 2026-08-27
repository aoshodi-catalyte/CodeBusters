import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from constants.drink_types import DrinkType
from constants.unit_conversions import convert
from database import Base
from drink_recipe.drink_ingredients_schema import DrinkRecipeIngredientSchema
from drink_recipe.drink_recipe_model import DrinkRecipe, RecipeIngredient
from repositories.drink_recipe_repository import DrinkRecipeRepository, map_enum_to_fk
from drink_recipe.drink_type_schema import DrinkTypeSchema
from ingredient.ingredient_schema import IngredientSchema

from exceptions.drink_recipe_exceptions import (
    DrinkTypeNotFoundError,
    DuplicateDrinkRecipeNameError,
    IngredientNotFoundError,
    UnitConversionError,
    DrinkRecipeNotFoundError
)

import models

# ---------------------------
# Test Database Setup
# ---------------------------

TEST_DB_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DB_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def repo(db):
    return DrinkRecipeRepository(db)

@pytest.fixture
def coffee_type(db):
    drink_type = DrinkTypeSchema(name="coffee")
    db.add(drink_type)
    db.commit()


# ---------------------------
# Tests
# ---------------------------

def test_map_enum_to_fk_success(db):
    drink_type = DrinkTypeSchema(name="coffee")
    db.add(drink_type)
    db.commit()
    fk_id = map_enum_to_fk(DrinkType.COFFEE, db)
    assert fk_id == drink_type.id


def test_map_enum_to_fk_missing_type(db):
    with pytest.raises(DrinkTypeNotFoundError):
        map_enum_to_fk(DrinkType.TEA, db)


def test_unsupported_unit_conversion():
    # convert() still raises ValueError
    with pytest.raises(ValueError):
        convert(1, "kg", "fl_oz")


def test_unexisting_unit_conversion():
    with pytest.raises(ValueError):
        convert(1, "banana", "fl_oz")


def test_create_drink_recipe(repo, db, coffee_type):

    milk = IngredientSchema(
        name="Milk",
        purchasing_cost=4.00,
        unit_amount=1.00,
        unit_of_measure="gal",
        vendor_id=1,
    )

    espresso = IngredientSchema(
        name="Espresso Beans",
        purchasing_cost=14.00,
        unit_amount=1.00,
        unit_of_measure="lb",
        vendor_id=1,
    )

    sugar = IngredientSchema(
        name="Sugar",
        purchasing_cost=2.50,
        unit_amount=4.00,
        unit_of_measure="lb",
        vendor_id=1,
    )

    db.add_all([milk, espresso, sugar])
    db.commit()

    recipe_model = DrinkRecipe(
        name="20oz Latte",
        description="Milk, espresso, sugar",
        ingredients=[
            RecipeIngredient(
                id=milk.id, quantity_used=16.00, unit_of_measure_used="fl_oz"
            ),
            RecipeIngredient(
                id=espresso.id, quantity_used=4.00, unit_of_measure_used="oz"
            ),
            RecipeIngredient(id=sugar.id, quantity_used=8.40, unit_of_measure_used="g"),
        ],
        active=True,
        type="coffee",
        markup_percentage=81,
    )

    created = repo.create_drink_recipe(recipe_model)

    assert created.production_cost == 4.01
    assert created.sale_price == 7.26


def test_duplicate_drink_recipe_name(repo, db, coffee_type):

    recipe_model = DrinkRecipe(
        name="Latte",
        description="desc",
        ingredients=[],
        active=True,
        type="coffee",
        markup_percentage=10,
    )

    repo.create_drink_recipe(recipe_model)

    with pytest.raises(DuplicateDrinkRecipeNameError):
        repo.create_drink_recipe(recipe_model)


def test_missing_ingredient(repo, db, coffee_type):

    recipe_model = DrinkRecipe(
        name="Bad Latte",
        description="desc",
        ingredients=[
            RecipeIngredient(id=999, quantity_used=1.0, unit_of_measure_used="g")
        ],
        active=True,
        type="coffee",
        markup_percentage=10,
    )

    with pytest.raises(IngredientNotFoundError):
        repo.create_drink_recipe(recipe_model)


def test_unit_conversion_failure(repo, db, coffee_type):

    ing = IngredientSchema(
        name="Milk",
        purchasing_cost=4.00,
        unit_amount=1.00,
        unit_of_measure="gal",
        vendor_id=1,
    )
    db.add(ing)
    db.commit()

    recipe_model = DrinkRecipe(
        name="Broken Latte",
        description="desc",
        ingredients=[
            RecipeIngredient(id=ing.id, quantity_used=1.0, unit_of_measure_used="banana")
        ],
        active=True,
        type="coffee",
        markup_percentage=10,
    )

    with pytest.raises(UnitConversionError):
        repo.create_drink_recipe(recipe_model)


def test_get_all_drink_recipes(repo, db):
    drink_type = DrinkTypeSchema(name="coffee")
    drink_type1 = DrinkTypeSchema(name="tea")
    db.add_all([drink_type, drink_type1])
    db.commit()

    milk = IngredientSchema(
        name="Milk",
        purchasing_cost=4.00,
        unit_amount=1.00,
        unit_of_measure="gal",
        vendor_id=1,
    )

    espresso = IngredientSchema(
        name="Espresso Beans",
        purchasing_cost=14.00,
        unit_amount=1.00,
        unit_of_measure="lb",
        vendor_id=1,
    )

    sugar = IngredientSchema(
        name="Sugar",
        purchasing_cost=2.50,
        unit_amount=4.00,
        unit_of_measure="lb",
        vendor_id=1,
    )

    matcha = IngredientSchema(
        name="Matcha Poweder",
        purchasing_cost=12.99,
        unit_amount=30.00,
        unit_of_measure="g",
        vendor_id=1,
    )

    db.add_all([milk, espresso, sugar, matcha])
    db.commit()

    recipe_model = DrinkRecipe(
        name="20oz Latte",
        description="Milk, espresso, sugar",
        ingredients=[
            RecipeIngredient(
                id=milk.id, quantity_used=16.00, unit_of_measure_used="fl_oz"
            ),
            RecipeIngredient(
                id=espresso.id, quantity_used=4.00, unit_of_measure_used="oz"
            ),
            RecipeIngredient(id=sugar.id, quantity_used=8.40, unit_of_measure_used="g"),
        ],
        active=True,
        type="coffee",
        markup_percentage=81,
    )

    recipe_model1 = DrinkRecipe(
        name="20oz Matcha Latte",
        description="Milk, macha powder, sugar",
        ingredients=[
            RecipeIngredient(
                id=milk.id, quantity_used=16.00, unit_of_measure_used="fl_oz"
            ),
            RecipeIngredient(
                id=matcha.id, quantity_used=4.00, unit_of_measure_used="g"
            ),
            RecipeIngredient(id=sugar.id, quantity_used=8.40, unit_of_measure_used="g"),
        ],
        active=True,
        type="tea",
        markup_percentage=81,
    )

    created = repo.create_drink_recipe(recipe_model)
    created1 = repo.create_drink_recipe(recipe_model1)

    created_list = [created, created1]

    assert created.production_cost == 4.01
    assert created.sale_price == 7.26

    assert created1.production_cost == 2.24
    assert created1.sale_price == 4.05

    assert len(created_list) == len(repo.get_all_drink_recipes())

def test_update_recipe_success(repo, db, coffee_type):
    milk = IngredientSchema(
        name="Milk",
        purchasing_cost=4.00,
        unit_amount=1.00,
        unit_of_measure="gal",
        vendor_id=1,
    )

    espresso = IngredientSchema(
        name="Espresso Beans",
        purchasing_cost=14.00,
        unit_amount=1.00,
        unit_of_measure="lb",
        vendor_id=1,
    )

    sugar = IngredientSchema(
        name="Sugar",
        purchasing_cost=2.50,
        unit_amount=4.00,
        unit_of_measure="lb",
        vendor_id=1,
    )

    db.add_all([milk, espresso, sugar])
    db.commit()

    recipe_model = DrinkRecipe(
        name="20oz Latte",
        description="Milk, espresso, sugar",
        ingredients=[
            RecipeIngredient(
                id=milk.id, quantity_used=16.00, unit_of_measure_used="fl_oz"
            ),
            RecipeIngredient(
                id=espresso.id, quantity_used=4.00, unit_of_measure_used="oz"
            ),
            RecipeIngredient(id=sugar.id, quantity_used=8.40, unit_of_measure_used="g"),
        ],
        active=True,
        type="coffee",
        markup_percentage=81,
    )

    created = repo.create_drink_recipe(recipe_model)

    updated_payload = DrinkRecipe(
        name="Updated Latte",
        description="new desc",
        active=False,
        type="coffee",
        markup_percentage=50,
        ingredients=[
            RecipeIngredient(
                id=milk.id,
                quantity_used=2.0,
                unit_of_measure_used="fl_oz"
            )
        ]
    )

    updated = repo.update_drink_recipe_by_id(created.id, updated_payload)

    assert updated.name == "Updated Latte"
    assert updated.description == "new desc"
    assert updated.active is False
    assert updated.markup_percentage == 50
    assert updated.production_cost > 0
    assert updated.sale_price > updated.production_cost

    # Ingredient associations replaced
    assoc = db.query(DrinkRecipeIngredientSchema).filter_by(drink_recipe_id=created.id).all()
    assert len(assoc) == 1
    assert assoc[0].quantity_used == 2.0


def test_update_recipe_not_found(repo, db, coffee_type):
    milk = IngredientSchema(
        name="Milk",
        purchasing_cost=4.00,
        unit_amount=1.00,
        unit_of_measure="gal",
        vendor_id=1,
    )

    espresso = IngredientSchema(
        name="Espresso Beans",
        purchasing_cost=14.00,
        unit_amount=1.00,
        unit_of_measure="lb",
        vendor_id=1,
    )

    sugar = IngredientSchema(
        name="Sugar",
        purchasing_cost=2.50,
        unit_amount=4.00,
        unit_of_measure="lb",
        vendor_id=1,
    )

    db.add_all([milk, espresso, sugar])
    db.commit()

    payload = DrinkRecipe(
        name="Latte",
        description="desc",
        active=True,
        type="coffee",
        markup_percentage=20,
        ingredients=[
            RecipeIngredient(
                id=milk.id, quantity_used=16.00, unit_of_measure_used="fl_oz"
            ),
            RecipeIngredient(
                id=espresso.id, quantity_used=4.00, unit_of_measure_used="oz"
            ),
            RecipeIngredient(id=sugar.id, quantity_used=8.40, unit_of_measure_used="g"),
        ],
    )

    with pytest.raises(DrinkRecipeNotFoundError):
        repo.update_drink_recipe_by_id(999, payload)


def test_update_recipe_ingredient_not_found(repo, db, coffee_type):
    milk = IngredientSchema(
        name="Milk",
        purchasing_cost=4.00,
        unit_amount=1.00,
        unit_of_measure="gal",
        vendor_id=1,
    )

    espresso = IngredientSchema(
        name="Espresso Beans",
        purchasing_cost=14.00,
        unit_amount=1.00,
        unit_of_measure="lb",
        vendor_id=1,
    )

    sugar = IngredientSchema(
        name="Sugar",
        purchasing_cost=2.50,
        unit_amount=4.00,
        unit_of_measure="lb",
        vendor_id=1,
    )

    db.add_all([milk, espresso, sugar])
    db.commit()

    recipe_model = DrinkRecipe(
        name="20oz Latte",
        description="Milk, espresso, sugar",
        ingredients=[
            RecipeIngredient(
                id=milk.id, quantity_used=16.00, unit_of_measure_used="fl_oz"
            ),
            RecipeIngredient(
                id=espresso.id, quantity_used=4.00, unit_of_measure_used="oz"
            ),
            RecipeIngredient(id=sugar.id, quantity_used=8.40, unit_of_measure_used="g"),
        ],
        active=True,
        type="coffee",
        markup_percentage=81,
    )

    created = repo.create_drink_recipe(recipe_model)

    bad_payload = DrinkRecipe(
        name="Latte",
        description="desc",
        active=True,
        type=DrinkType.COFFEE,
        markup_percentage=20,
        ingredients=[
            RecipeIngredient(
                id=999,  # invalid ingredient
                quantity_used=1.0,
                unit_of_measure_used="cup"
            )
        ]
    )

    with pytest.raises(IngredientNotFoundError):
        repo.update_drink_recipe_by_id(created.id, bad_payload)

def test_update_recipe_duplicate_name(repo, db, coffee_type):
    milk = IngredientSchema(
        name="Milk",
        purchasing_cost=4.00,
        unit_amount=1.00,
        unit_of_measure="gal",
        vendor_id=1,
    )

    db.add(milk)
    db.commit()

    recipe_model = DrinkRecipe(
        name="20oz Latte",
        description="Milk, espresso, sugar",
        ingredients=[
            RecipeIngredient(
                id=milk.id, quantity_used=16.00, unit_of_measure_used="fl_oz"
            )
        ],
        active=True,
        type="coffee",
        markup_percentage=81,
    )

    recipe_model1 = DrinkRecipe(
        name="20oz Mocha",
        description="Milk, espresso, sugar",
        ingredients=[
            RecipeIngredient(
                id=milk.id, quantity_used=16.00, unit_of_measure_used="fl_oz"
            )
        ],
        active=True,
        type="coffee",
        markup_percentage=81,
    )

    r1 = repo.create_drink_recipe(recipe_model)
    r2 = repo.create_drink_recipe(recipe_model1)

    payload = DrinkRecipe(
        name=r1.name,  # duplicate name
        description="desc",
        active=True,
        type="coffee",
        markup_percentage=20,
        ingredients=[
            RecipeIngredient(
                id=milk.id,
                quantity_used=1.0,
                unit_of_measure_used="cup"
            )
        ]
    )

    with pytest.raises(DuplicateDrinkRecipeNameError):
        repo.update_drink_recipe_by_id(r2.id, payload)


def test_update_recipe_drink_type_not_found(repo, db, coffee_type):
    milk = IngredientSchema(
        name="Milk",
        purchasing_cost=4.00,
        unit_amount=1.00,
        unit_of_measure="gal",
        vendor_id=1,
    )

    espresso = IngredientSchema(
        name="Espresso Beans",
        purchasing_cost=14.00,
        unit_amount=1.00,
        unit_of_measure="lb",
        vendor_id=1,
    )

    sugar = IngredientSchema(
        name="Sugar",
        purchasing_cost=2.50,
        unit_amount=4.00,
        unit_of_measure="lb",
        vendor_id=1,
    )

    db.add_all([milk, espresso, sugar])
    db.commit()

    recipe_model = DrinkRecipe(
        name="20oz Latte",
        description="Milk, espresso, sugar",
        ingredients=[
            RecipeIngredient(
                id=milk.id, quantity_used=16.00, unit_of_measure_used="fl_oz"
            ),
            RecipeIngredient(
                id=espresso.id, quantity_used=4.00, unit_of_measure_used="oz"
            ),
            RecipeIngredient(id=sugar.id, quantity_used=8.40, unit_of_measure_used="g"),
        ],
        active=True,
        type="coffee",
        markup_percentage=81,
    )

    created = repo.create_drink_recipe(recipe_model)

    # Remove drink types
    db.query(DrinkTypeSchema).delete()
    db.commit()

    bad_payload = DrinkRecipe(
        name="Latte",
        description="desc",
        active=True,
        type="coffee",
        markup_percentage=20,
        ingredients=[
            RecipeIngredient(
                id=milk.id,
                quantity_used=1.0,
                unit_of_measure_used="cup"
            )
        ]
    )

    with pytest.raises(DrinkTypeNotFoundError):
        repo.update_drink_recipe_by_id(created.id, bad_payload)


