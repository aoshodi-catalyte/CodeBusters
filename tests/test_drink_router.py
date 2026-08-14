import pytest
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

    drink_type = DrinkTypeSchema(name="coffee")
    ing1 = IngredientSchema(
        name="Sugar",
        purchasing_cost=0.50,
        unit_amount=10.00,
        unit_of_measure="g",
        vendor_id=1
    )
    ing2 = IngredientSchema(
        name="Milk",
        purchasing_cost=0.30,
        unit_amount=50.00,
        unit_of_measure="ml",
        vendor_id=1
    )

    db.add_all([drink_type, ing1, ing2])
    db.commit()

    payload = {
        "name": "Sweet Coffee",
        "description": "Coffee with sugar and milk",
        "ingredients": [
            {"id": ing1.id, "quantity_used": 5.00, "unit_of_measure_used": "g"},
            {"id": ing2.id, "quantity_used": 30.00, "unit_of_measure_used": "ml"}
        ],
        "active": True,
        "type": "coffee",
        "markup_percentage": 20
    }

    response = client.post("/drink_recipes/", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "Sweet Coffee"
    assert data["type"] == "coffee"
    assert len(data["ingredients"]) == 2

    sugar = data["ingredients"][0]
    milk = data["ingredients"][1]

    assert sugar["name"] == "Sugar"
    assert sugar["quantity_used"] == 5.00
    assert sugar["unit_of_measure_used"] == "g"

    assert milk["name"] == "Milk"
    assert milk["quantity_used"] == 30.00
    assert milk["unit_of_measure_used"] == "ml"

def test_get_drink_recipe_by_id(client, db):
    drink_type = DrinkTypeSchema(name="tea")
    db.add(drink_type)
    db.commit()

    recipe = {
        "name": "Plain Tea",
        "description": "Simple tea",
        "ingredients": [],
        "active": True,
        "type": "tea",
        "markup_percentage": 10
    }

    created = client.post("/drink_recipes/", json=recipe).json()
    recipe_id = created["id"]

    response = client.get(f"/drink_recipes/{recipe_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == recipe_id
    assert data["name"] == "Plain Tea"
    assert data["ingredients"] == []

def test_get_all_drink_recipes(client, db):
    drink_type = DrinkTypeSchema(name="coffee")
    db.add(drink_type)
    db.commit()

    r1 = {
        "name": "A",
        "description": "desc",
        "ingredients": [],
        "active": True,
        "type": "coffee",
        "markup_percentage": 10
    }

    r2 = {
        "name": "B",
        "description": "desc",
        "ingredients": [],
        "active": True,
        "type": "coffee",
        "markup_percentage": 15
    }

    client.post("/drink_recipes/", json=r1)
    client.post("/drink_recipes/", json=r2)

    response = client.get("/drink_recipes/")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "A"
    assert data[1]["name"] == "B"
