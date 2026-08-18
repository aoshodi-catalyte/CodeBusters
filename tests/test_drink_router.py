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
        purchasing_cost=5.50,
        unit_amount=10.00,
        unit_of_measure="lb",
        vendor_id=1
    )
    ing2 = IngredientSchema(
        name="Milk",
        purchasing_cost=7.30,
        unit_amount=1.00,
        unit_of_measure="gal",
        vendor_id=1
    )

    db.add_all([drink_type, ing1, ing2])
    db.commit()

    payload = {
        "name": "Sweet Coffee",
        "description": "Coffee with sugar and milk",
        "ingredients": [
            {"id": ing1.id, "quantity_used": 5.00, "unit_of_measure_used": "g"},
            {"id": ing2.id, "quantity_used": 16.00, "unit_of_measure_used": "fl_oz"}
        ],
        "active": True,
        "type": "coffee",
        "markup_percentage": 100
    }

    response = client.post("/drink_recipes/", json=payload)
    assert response.status_code == 201

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
    assert milk["quantity_used"] == 16.00
    assert milk["unit_of_measure_used"] == "fl_oz"

    assert data["production_cost"] == 0.92
    assert data["sale_price"] == 1.84


def test_duplicate_drink_name_rejected(client, db):
    """POST /drink_recipes should reject duplicate recipe names."""

    drink_type = DrinkTypeSchema(name="coffee")
    db.add(drink_type)
    db.commit()

    recipe_payload = {
        "name": "Sweet Coffee",
        "description": "Coffee with sugar",
        "ingredients": [],
        "active": True,
        "type": "coffee",
        "markup_percentage": 20
    }

    # First creation should succeed
    response1 = client.post("/drink_recipes/", json=recipe_payload)
    assert response1.status_code == 201

    # Second creation with same name should fail
    response2 = client.post("/drink_recipes/", json=recipe_payload)

    assert response2.status_code == 409
    assert "already exists" in response2.json()["detail"].lower()


def test_negative_quantity_used(client, db):
    """POST /drink_recipes should rejcet ingredients with a negative quantity_used."""
    drink_type = DrinkTypeSchema(name="tea")
    ing2 = IngredientSchema(
        name="Milk",
        purchasing_cost=7.30,
        unit_amount=1.00,
        unit_of_measure="gal",
        vendor_id=1
    )

    db.add_all([drink_type, ing2])
    db.commit()

    payload = {
        "name": "Negative Quantity Used",
        "description": "Should fail due to negative quantity",
        "active": True,
        "type": "tea",
        "ingredients": [ {"id": ing2.id, "quantity_used": -16.00, "unit_of_measure_used": "oz"} ],
        "markup_percentage": 20
    }

    response = client.post("/drink_recipes/", json=payload)

    assert response.status_code == 422
    assert any("input should be greater than 0" in err["msg"].lower()
           for err in response.json()["detail"])


def test_create_recipe_invalid_ingredient_id(client, db):
    """POST /drink_recipes should reject recipes containing invalid ingredient IDs."""

    # Create a drink type so the recipe is otherwise valid
    drink_type = DrinkTypeSchema(name="coffee")
    db.add(drink_type)
    db.commit()

    payload = {
        "name": "Invalid Ingredient Drink",
        "description": "Should fail due to bad ingredient ID",
        "active": True,
        "type": "coffee",
        "ingredients": [
            {
                "id": 9999,  # <-- does not exist
                "quantity_used": 10,
                "unit_of_measure_used": "g"
            }
        ],
        "markup_percentage": 20
    }

    response = client.post("/drink_recipes/", json=payload)

    assert response.status_code == 409
    assert "ingredient id" in response.json()["detail"].lower()
    assert "not found" in response.json()["detail"].lower()


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

def test_get_drink_recipe_by_id_not_found(client, db):
    response = client.get(f"/drink_recipes/{9999}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Drink recipe not found"

@pytest.fixture
def drink_types(db):
    types = [
        DrinkTypeSchema(name="coffee"),
        DrinkTypeSchema(name="tea"),
        DrinkTypeSchema(name="soda"),
        DrinkTypeSchema(name="other"),
    ]
    db.add_all(types)
    db.commit()
    return types

def test_invalid_drink_type(client, db, drink_types):
    r1 = {
        "name": "A",
        "description": "desc",
        "ingredients": [],
        "active": True,
        "type": "not valid",
        "markup_percentage": 10
    }

    response = client.post("/drink_recipes/", json=r1)
    assert response.status_code == 422
    assert any("Invalid drink type: not valid. Valid types are: ['coffee', 'tea', 'soda', 'other']" in err["msg"]
           for err in response.json()["detail"])


def test_all_valid_drink_types(client, db, drink_types):
    r1 = {
        "name": "A",
        "description": "desc",
        "ingredients": [],
        "active": True,
        "type": "Coffee",
        "markup_percentage": 10
    }

    r2 = {
        "name": "B",
        "description": "desc",
        "ingredients": [],
        "active": True,
        "type": "tea",
        "markup_percentage": 15
    }

    r3 = {
            "name": "C",
            "description": "desc",
            "ingredients": [],
            "active": True,
            "type": "Soda",
            "markup_percentage": 20
        }

    r4 = {
            "name": "D",
            "description": "desc",
            "ingredients": [],
            "active": True,
            "type": "other",
            "markup_percentage": 25
        }

    client.post("/drink_recipes/", json=r1)
    client.post("/drink_recipes/", json=r2)
    client.post("/drink_recipes/", json=r3)
    client.post("/drink_recipes/", json=r4)

    response = client.get("/drink_recipes/")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 4
    assert data[0]["name"] == "A"
    assert data[1]["name"] == "B"
    assert data[2]["name"] == "C"
    assert data[3]["name"] == "D"

    assert data[0]["type"] == "coffee"
    assert data[1]["type"] == "tea"
    assert data[2]["type"] == "soda"
    assert data[3]["type"] == "other"

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
