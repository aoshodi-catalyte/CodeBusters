import pytest
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app # type: ignore
from database import Base, get_db # type: ignore
from drink_recipe.drink_type_schema import DrinkTypeSchema # type: ignore
from ingredient.ingredient_schema import IngredientSchema # type: ignore


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
    """Fresh in-memory DB for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db):
    """FastAPI TestClient using the test DB."""
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    yield client
    app.dependency_overrides.clear()


# ---------------------------
# Tests
# ---------------------------

def test_create_drink_recipe(client, db):
    """POST /drink_recipes should create a recipe."""

    # Insert drink type + ingredients
    drink_type = DrinkTypeSchema(name="coffee")
    ing1 = IngredientSchema(name="Sugar", purchasing_cost=Decimal("0.50"),
                            unit_amount=Decimal("10.00"), unit_of_measure="g", vendor_id=1)
    ing2 = IngredientSchema(name="Milk", purchasing_cost=Decimal("0.30"),
                            unit_amount=Decimal("50.00"), unit_of_measure="ml", vendor_id=1)

    db.add_all([drink_type, ing1, ing2])
    db.commit()

    payload = {
        "name": "Sweet Coffee",
        "description": "Coffee with sugar and milk",
        "ingredients": [ing1.id, ing2.id],
        "active": True,
        "type": "coffee",
        "production_cost": "2.50",
        "markup_percentage": "20",
        "sale_price": "3.00"
    }

    response = client.post("/drink_recipes/", json=payload)

    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "Sweet Coffee"
    assert data["type"] == "coffee"
    assert len(data["ingredients"]) == 2
    assert data["ingredients"][0]["name"] == "Sugar"
    assert data["ingredients"][1]["name"] == "Milk"


def test_get_drink_recipe_by_id(client, db):
    """GET /drink_recipes/{id} should return a recipe."""

    drink_type = DrinkTypeSchema(name="tea")
    db.add(drink_type)
    db.commit()

    recipe = {
        "name": "Plain Tea",
        "description": "Simple tea",
        "ingredients": [],
        "active": True,
        "type": "tea",
        "production_cost": "1.00",
        "markup_percentage": 10,
        "sale_price": "2.00"
    }

    created = client.post("/drink_recipes/", json=recipe).json()
    recipe_id = created["id"]

    response = client.get(f"/drink_recipes/{recipe_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == recipe_id
    assert data["name"] == "Plain Tea"


def test_get_drink_recipe_not_found(client):
    """GET /drink_recipes/{id} should return 404 if missing."""

    response = client.get("/drink_recipes/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Drink recipe not found"

def test_get_all_drink_recipes(client, db):
    """GET /drink_recipes should return all recipes."""

    drink_type = DrinkTypeSchema(name="coffee")
    db.add(drink_type)
    db.commit()

    r1 = {
        "name": "A",
        "description": "desc",
        "ingredients": [],
        "active": True,
        "type": "coffee",
        "production_cost": "1.00",
        "markup_percentage": 10,
        "sale_price": "2.00"
    }

    r2 = {
        "name": "B",
        "description": "desc",
        "ingredients": [],
        "active": True,
        "type": "coffee",
        "production_cost": "1.50",
        "markup_percentage": 15,
        "sale_price": "3.00"
    }

    client.post("/drink_recipes/", json=r1)
    client.post("/drink_recipes/", json=r2)

    response = client.get("/drink_recipes/")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "A"
    assert data[1]["name"] == "B"
