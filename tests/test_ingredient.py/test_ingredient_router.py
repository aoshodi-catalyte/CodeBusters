from decimal import Decimal
from unittest.mock import MagicMock

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import pytest
from database import Base, get_db
from constants.INGREDIENT_TYPES import UnitOfMeasure, CafeAllergen
from vendor.vendor_schema import Vendor
from ingredient.ingredient_schema import IngredientSchema
from ingredient.ingredient_exceptions import (
    IngredientAlreadyExistsError,
    IngredientConstraintError,
    VendorNotFoundError,
)
from ingredient.ingredient_repository import get_ingredient_by_id
from ingredient.ingredient_router import router
import ingredient.ingredient_router as ingredient_router


# ============================================================
# TEST APPLICATION
# ============================================================

app = FastAPI()
app.include_router(router)


@pytest.fixture
def client():
    return TestClient(app)

# ============================================================
# TEST HELPERS
# ============================================================

@pytest.fixture
def client_with_real_db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Import models so they are registered with Base.metadata
    from vendor.vendor_schema import Vendor
    from ingredient.ingredient_model import Ingredient

    Base.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )


# ============================================================
# DATABASE OVERRIDE
# ============================================================

def override_get_db():
    """
    Provide a fake database session for router tests.

    The repository function is mocked in these tests, so we
    do not need a real database.
    """
    db = MagicMock()
    yield db


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


# ============================================================
# TEST DATA
# ============================================================

# Get valid enum values without assuming their exact names.
VALID_UNIT_OF_MEASURE = next(iter(UnitOfMeasure)).value
VALID_ALLERGEN = next(iter(CafeAllergen)).value


def valid_ingredient_payload():
    """
    Return a valid ingredient request body.
    """
    return {
        "active": True,
        "name": "Flour",
        "purchasing_cost": "10.50",
        "unit_amount": "25.00",
        "unit_of_measure": VALID_UNIT_OF_MEASURE,
        "allergens": [VALID_ALLERGEN],
        "vendor_id": 1,
    }


def valid_ingredient_response():
    """
    Return the data that the mocked repository would return.
    """
    payload = valid_ingredient_payload()

    return {
        "id": 1,
        "name": payload["name"],
        "active": payload["active"],
        "purchasing_cost": Decimal(payload["purchasing_cost"]),
        "unit_amount": Decimal(payload["unit_amount"]),
        "unit_of_measure": payload["unit_of_measure"],
        "allergens": [
            {"name": allergen.title()}
            for allergen in payload["allergens"]
        ],
        "vendor_id": payload["vendor_id"],
    }


# ============================================================
# 1. SUCCESSFUL CREATION
# ============================================================

def test_create_ingredient_success(monkeypatch):
    """
    Test that a valid ingredient is successfully created.
    """

    expected_ingredient = valid_ingredient_response()

    mock_create = MagicMock(return_value=expected_ingredient)

    monkeypatch.setattr(
        ingredient_router,
        "create_ingredient",
        mock_create,
    )

    response = client.post(
        "/ingredients/",
        json=valid_ingredient_payload(),
    )
    assert response.status_code == 201

    data = response.json()

    assert data["id"] == 1
    assert data["name"] == "Flour"
    assert data["active"] is True
    assert data["vendor_id"] == 1

    mock_create.assert_called_once()


# ============================================================
# 2. VENDOR DOES NOT EXIST
# ============================================================

def test_create_ingredient_vendor_not_found(monkeypatch):
    """
    Test that a missing vendor returns HTTP 404.
    """

    mock_create = MagicMock(
        side_effect=VendorNotFoundError(999)
    )

    monkeypatch.setattr(
        ingredient_router,
        "create_ingredient",
        mock_create,
    )

    payload = valid_ingredient_payload()
    payload["vendor_id"] = 999

    response = client.post(
        "/ingredients/",
        json=payload,
    )

    assert response.status_code == 404

    data = response.json()

    assert data["detail"]["error"] == "vendor_not_found"


# ============================================================
# 3. DUPLICATE INGREDIENT
# ============================================================

def test_create_ingredient_already_exists(monkeypatch):
    """
    Test that attempting to create a duplicate ingredient
    returns HTTP 409.
    """

    mock_create = MagicMock(
        side_effect=IngredientAlreadyExistsError("Flour")
    )

    monkeypatch.setattr(
        ingredient_router,
        "create_ingredient",
        mock_create,
    )

    response = client.post(
        "/ingredients/",
        json=valid_ingredient_payload(),
    )

    assert response.status_code == 409

    data = response.json()

    assert data["detail"]["error"] == "ingredient_already_exists"


# ============================================================
# 4. DATABASE CONSTRAINT ERROR
# ============================================================

def test_create_ingredient_constraint_error(monkeypatch):
    """
    Test that a database constraint violation returns HTTP 409.
    """

    mock_create = MagicMock(
        side_effect=IngredientConstraintError(
            "ck_ingredient_unit_amount_positive"
        )
    )

    monkeypatch.setattr(
        ingredient_router,
        "create_ingredient",
        mock_create,
    )

    response = client.post(
        "/ingredients/",
        json=valid_ingredient_payload(),
    )

    assert response.status_code == 409

    data = response.json()

    assert data["detail"]["error"] == "database_constraint_violation"


# ============================================================
# 5. UNEXPECTED DATABASE ERROR
# ============================================================

def test_create_ingredient_database_error(monkeypatch):
    """
    Test that an unexpected SQLAlchemy error returns HTTP 500.
    """

    mock_create = MagicMock(
        side_effect=SQLAlchemyError("Database connection failed")
    )

    monkeypatch.setattr(
        ingredient_router,
        "create_ingredient",
        mock_create,
    )

    response = client.post(
        "/ingredients/",
        json=valid_ingredient_payload(),
    )

    assert response.status_code == 500

    data = response.json()

    assert data["detail"]["error"] == "database_error"

    assert (
        data["detail"]["message"]
        == "An unexpected database error occurred while creating the ingredient."
    )


# ============================================================
# 6. INVALID VENDOR ID
# ============================================================

def test_create_ingredient_invalid_vendor_id(monkeypatch):
    """
    Test that vendor_id must be greater than zero.
    """

    payload = valid_ingredient_payload()
    payload["vendor_id"] = 0

    response = client.post(
        "/ingredients/",
        json=payload,
    )

    assert response.status_code == 422


# ============================================================
# 7. NEGATIVE PURCHASING COST
# ============================================================

def test_create_ingredient_negative_purchasing_cost(monkeypatch):
    """
    Test that purchasing_cost cannot be negative.
    """

    payload = valid_ingredient_payload()
    payload["purchasing_cost"] = "-5.00"

    response = client.post(
        "/ingredients/",
        json=payload,
    )

    assert response.status_code == 422


# ============================================================
# 8. ZERO UNIT AMOUNT
# ============================================================

def test_create_ingredient_zero_unit_amount(monkeypatch):
    """
    Test that unit_amount must be greater than zero.
    """

    payload = valid_ingredient_payload()
    payload["unit_amount"] = "0"

    response = client.post(
        "/ingredients/",
        json=payload,
    )

    assert response.status_code == 422


# ============================================================
# 9. MISSING REQUIRED FIELD
# ============================================================

def test_create_ingredient_missing_name(monkeypatch):
    """
    Test that name is required.
    """

    payload = valid_ingredient_payload()
    del payload["name"]

    response = client.post(
        "/ingredients/",
        json=payload,
    )

    assert response.status_code == 422


# ============================================================
# 10. EMPTY INGREDIENT NAME
# ============================================================

def test_create_ingredient_empty_name(monkeypatch):
    """
    Test that ingredient name cannot be empty.
    """

    payload = valid_ingredient_payload()
    payload["name"] = ""

    response = client.post(
        "/ingredients/",
        json=payload,
    )

    assert response.status_code == 422
# ============================================================
# TEST 11
# READ ALL INGREDIENTS RETURNS 200
# ============================================================

def test_read_all_ingredients_returns_200(monkeypatch):
    response = client.get("/ingredients/all")

    assert response.status_code == 200


# ============================================================
# TEST 12
# READ ALL INGREDIENTS RETURNS EMPTY LIST
# ============================================================

def test_read_all_ingredients_returns_empty_list(monkeypatch):
    response = client.get("/ingredients/all")

    assert response.status_code == 200
    assert response.json()["ingredients"] == []


# ============================================================
# TEST 13
# READ ALL INGREDIENTS RETURNS INGREDIENTS
# ============================================================

def test_read_all_ingredients_returns_ingredients(
    monkeypatch,
):
    ingredients = [
        {
            "id": 1,
            "name": "Flour",
            "active": True,
            "purchasing_cost": 10.00,
            "unit_amount": 25.00,
            "unit_of_measure": VALID_UNIT_OF_MEASURE,
            "allergens": [
                {"name": VALID_ALLERGEN}
            ],
            "vendor_id": 1,
        }
    ]

    monkeypatch.setattr(
        ingredient_router,
        "get_all_ingredients",
        lambda db: ingredients,
    )

    response = client.get("/ingredients/all")

    assert response.status_code == 200
    assert response.json()["message"] == (
        "These are all the ingredients in your inventory!"
    )
    assert len(response.json()["ingredients"]) == 1
    assert response.json()["ingredients"][0]["name"] == "Flour"
    # ============================================================
# TEST 14
# READ INGREDIENT BY ID SUCCESSFULLY
# ============================================================

def test_read_ingredient_returns_ingredient(monkeypatch):
    """
    Test that a valid ingredient ID returns the ingredient.
    """
    ingredient = valid_ingredient_response()

    mock_get = MagicMock(
        return_value=ingredient
    )

    monkeypatch.setattr(
        ingredient_router,
        "get_ingredient_by_id",
        mock_get,
    )

    response = client.get("/ingredients/1")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 1
    assert data["name"] == "Flour"
    assert data["vendor_id"] == 1

    mock_get.assert_called_once()


# ============================================================
# TEST 15
# INGREDIENT NOT FOUND
# ============================================================

def test_read_ingredient_not_found(monkeypatch):
    """
    Test that a nonexistent ingredient ID returns HTTP 404.
    """
    mock_get = MagicMock(
        return_value=None
    )

    monkeypatch.setattr(
        ingredient_router,
        "get_ingredient_by_id",
        mock_get,
    )

    response = client.get("/ingredients/999")

    assert response.status_code == 404

    data = response.json()

    assert data["detail"]["error"] == "ingredient_not_found"

    mock_get.assert_called_once()


# ============================================================
# TEST 16
# INVALID INGREDIENT ID
# ============================================================

def test_read_ingredient_invalid_id():
    """
    Test that a non-integer ingredient ID returns HTTP 422.
    """
    response = client.get("/ingredients/abc")

    assert response.status_code == 422

def test_read_all_ingredients_integration():
    """
    Test the complete GET /ingredients/all request flow.

    This test uses a real in-memory SQLite database and exercises
    the FastAPI router, repository, database query, and response.
    """

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(bind=engine)

    def override_real_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    # Tell FastAPI to use the real test database.
    app.dependency_overrides[get_db] = override_real_db

    try:
        # Create a database session for seeding test data.
        db = TestingSessionLocal()

        # --------------------------------------------
        # Create vendor
        # --------------------------------------------

        vendor = Vendor(
            name="Integration Vendor",
            contact_name="Test Person",
            contact_role="Sales",
            email="integration@test.com",
            phone="3125559999",
            active=True,
        )

        db.add(vendor)
        db.commit()
        db.refresh(vendor)

        # --------------------------------------------
        # Create ingredient
        # --------------------------------------------

        ingredient = IngredientSchema(
            active=True,
            name="Integration Flour",
            purchasing_cost=10.00,
            unit_amount=25.00,
            unit_of_measure="lb",
            vendor_id=vendor.id,
        )

        db.add(ingredient)
        db.commit()

        # --------------------------------------------
        # Make real HTTP request
        # --------------------------------------------

        test_client = TestClient(app)

        response = test_client.get("/ingredients/all")

        # --------------------------------------------
        # Assertions
        # --------------------------------------------

        assert response.status_code == 200

        data = response.json()

        assert data["message"] == (
            "These are all the ingredients in your inventory!"
        )

        assert len(data["ingredients"]) == 1

        assert data["ingredients"][0]["name"] == "Integration Flour"

    finally:
        app.dependency_overrides.clear()

        if "db" in locals():
            db.close()

        Base.metadata.drop_all(bind=engine)
        engine.dispose()
    # ============================================================
# TEST 17
# UPDATE INGREDIENT SUCCESSFULLY
# ============================================================

def test_update_ingredient_success(monkeypatch):
    """
    Test that a valid ingredient update returns HTTP 200
    and the updated ingredient.
    """
    updated_ingredient = valid_ingredient_response()
    updated_ingredient["name"] = "Updated Flour"
    updated_ingredient["purchasing_cost"] = Decimal("12.50")

    mock_update = MagicMock(return_value=updated_ingredient)

    monkeypatch.setattr(
        ingredient_router,
        "update_ingredient",
        mock_update,
    )

    payload = valid_ingredient_payload()
    payload["name"] = "Updated Flour"
    payload["purchasing_cost"] = "12.50"

    response = client.put(
        "/ingredients/1",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 1
    assert data["name"] == "Updated Flour"
    assert data["purchasing_cost"] == 12.50
    assert data["vendor_id"] == 1

    mock_update.assert_called_once()


# ============================================================
# TEST 18
# UPDATE INGREDIENT NOT FOUND
# ============================================================

def test_update_ingredient_not_found(monkeypatch):
    """
    Test that updating an ingredient that does not exist
    returns HTTP 404.
    """
    mock_update = MagicMock(return_value=None)

    monkeypatch.setattr(
        ingredient_router,
        "update_ingredient",
        mock_update,
    )

    response = client.put(
        "/ingredients/999",
        json=valid_ingredient_payload(),
    )

    assert response.status_code == 404

    data = response.json()

    assert data["detail"]["error"] == "ingredient_not_found"

    mock_update.assert_called_once()


# ============================================================
# TEST 19
# UPDATE INGREDIENT CONSTRAINT ERROR
# ============================================================

def test_update_ingredient_constraint_error(monkeypatch):
    """
    Test that a database constraint violation during an
    ingredient update returns HTTP 409.
    """
    mock_update = MagicMock(
        side_effect=IngredientConstraintError(
            "ck_ingredient_purchasing_cost_non_negative"
        )
    )

    monkeypatch.setattr(
        ingredient_router,
        "update_ingredient",
        mock_update,
    )

    response = client.put(
        "/ingredients/1",
        json=valid_ingredient_payload(),
    )

    assert response.status_code == 409

    data = response.json()

    assert data["detail"]["error"] == (
        "database_constraint_violation"
    )

    mock_update.assert_called_once()