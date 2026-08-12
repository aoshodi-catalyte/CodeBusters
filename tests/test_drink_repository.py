import pytest
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from drink_recipe.drink_recipe_repository import ( # type: ignore
    DrinkRecipeRepository,
    map_enum_to_fk
)
from drink_recipe.drink_recipe_model import DrinkRecipe # type: ignore
from drink_recipe.drink_recipe_schema import DrinkRecipeSchema # type: ignore
from drink_recipe.drink_type_schema import DrinkTypeSchema # type: ignore
from ingredient.ingredient_schema import IngredientSchema # type: ignore
from constants.DRINK_TYPES import DrinkType # type: ignore
from database import Base # type: ignore


# ---------------------------
# Test Database Setup
# ---------------------------

TEST_DB_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


@pytest.fixture
def db():
    """Creates a fresh in-memory DB for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def repo(db):
    """Repository instance using the test DB."""
    return DrinkRecipeRepository(db)


# ---------------------------
# Tests
# ---------------------------

def test_map_enum_to_fk_success(db):
    """map_enum_to_fk should return the correct FK ID."""
    drink_type = DrinkTypeSchema(name="coffee")
    db.add(drink_type)
    db.commit()

    fk_id = map_enum_to_fk(DrinkType.COFFEE, db)
    assert fk_id == drink_type.id


def test_map_enum_to_fk_missing_type(db):
    """map_enum_to_fk should raise ValueError if type not found."""
    with pytest.raises(ValueError):
        map_enum_to_fk(DrinkType.TEA, db)


def test_create_drink_recipe(repo, db):
    """Repository should create a drink recipe with correct fields."""

    # Insert drink type
    drink_type = DrinkTypeSchema(name="coffee")
    db.add(drink_type)
    db.commit()

    # Insert ingredients
    ing1 = IngredientSchema(name="Sugar", purchasing_cost=Decimal("0.50"),
                            unit_amount=Decimal("10.00"), unit_of_measure="g", vendor_id=1)
    ing2 = IngredientSchema(name="Milk", purchasing_cost=Decimal("0.30"),
                            unit_amount=Decimal("50.00"), unit_of_measure="ml", vendor_id=1)

    db.add_all([ing1, ing2])
    db.commit()

    recipe_model = DrinkRecipe(
        name="Sweet Coffee",
        description="Coffee with sugar and milk",
        ingredients=[ing1.id, ing2.id],
        active=True,
        type="coffee",
        production_cost=Decimal("2.50"),
        markup_percentage=20,
        sale_price=Decimal("3.00"),
    )

    created = repo.create_drink_recipe(recipe_model)

    assert created.id is not None
    assert created.name == "Sweet Coffee"
    assert created.type_id == drink_type.id
    assert len(created.ingredients) == 2
    assert created.ingredients[0].name == "Sugar"
    assert created.ingredients[1].name == "Milk"


def test_create_drink_recipe_missing_ingredient(repo, db):
    """Missing ingredient IDs should simply be skipped."""

    drink_type = DrinkTypeSchema(name="tea")
    db.add(drink_type)
    db.commit()

    recipe_model = DrinkRecipe(
        name="Plain Tea",
        description="Tea with no valid ingredients",
        ingredients=[999],  # does not exist
        active=True,
        type="tea",
        production_cost=Decimal("1.00"),
        markup_percentage=10,
        sale_price=Decimal("2.00"),
    )

    created = repo.create_drink_recipe(recipe_model)

    assert created.id is not None
    assert created.ingredients == []


def test_get_drink_recipe_by_id(repo, db):
    """Repository should retrieve a drink recipe by ID."""

    drink_type = DrinkTypeSchema(name="coffee")
    db.add(drink_type)
    db.commit()

    recipe = DrinkRecipeSchema(
        name="Test Coffee",
        description="Test",
        active=True,
        type_id=drink_type.id,
        production_cost=Decimal("1.00"),
        markup_percentage=10,
        sale_price=Decimal("2.00"),
    )

    db.add(recipe)
    db.commit()

    fetched = repo.get_drink_recipe_by_id(recipe.id)
    assert fetched is not None
    assert fetched.name == "Test Coffee"


def test_get_all_drink_recipes(repo, db):
    """Repository should return all drink recipes."""

    drink_type = DrinkTypeSchema(name="coffee")
    db.add(drink_type)
    db.commit()

    r1 = DrinkRecipeSchema(
        name="A",
        description="desc",
        active=True,
        type_id=drink_type.id,
        production_cost=Decimal("1.00"),
        markup_percentage=10,
        sale_price=Decimal("2.00"),
    )

    r2 = DrinkRecipeSchema(
        name="B",
        description="desc",
        active=True,
        type_id=drink_type.id,
        production_cost=Decimal("1.50"),
        markup_percentage=15,
        sale_price=Decimal("3.00"),
    )

    db.add_all([r1, r2])
    db.commit()

    recipes = repo.get_all_drink_recipes()
    assert len(recipes) == 2
    assert recipes[0].name == "A"
    assert recipes[1].name == "B"
