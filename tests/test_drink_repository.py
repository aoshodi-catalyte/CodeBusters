import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from drink_recipe.drink_recipe_repository import DrinkRecipeRepository, map_enum_to_fk
from drink_recipe.drink_recipe_model import DrinkRecipe, RecipeIngredient
from drink_recipe.drink_type_schema import DrinkTypeSchema
from ingredient.ingredient_schema import IngredientSchema
from constants.drink_types import DrinkType
from database import Base
from constants.unit_conversions import convert

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
    with pytest.raises(ValueError):
        map_enum_to_fk(DrinkType.TEA, db)


def test_unsupported_unit_conversion():
    with pytest.raises(ValueError):
        convert(1, "kg", "fl_oz")


def test_unexisting_unit_conversion():
    with pytest.raises(ValueError):
        convert(1, "banana", "fl_oz")


def test_create_drink_recipe(repo, db):
    drink_type = DrinkTypeSchema(name="coffee")
    db.add(drink_type)
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

    # Production cost:
    # Milk: 0.50
    # Espresso: 3.50
    # Sugar: 0.01
    # Total: 4.01
    assert created.production_cost == 4.01

    # Sale price = 4.01 * 1.81 = 7.2581 → 7.26
    assert created.sale_price == 7.26
