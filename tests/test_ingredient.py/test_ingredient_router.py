"""Tests for the ingredient API router."""

from decimal import Decimal
from unittest.mock import MagicMock

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from constants.INGREDIENT_TYPES import CafeAllergen, UnitOfMeasure
from database import Base, get_db
from ingredient.ingredient_exceptions import (
    IngredientAlreadyExistsError,
    IngredientConstraintError,
    VendorNotFoundError,
)
from ingredient.ingredient_router import router
from ingredient.ingredient_schema import IngredientSchema
import ingredient.ingredient_router as ingredient_router
from vendor.vendor_schema import Vendor


app = FastAPI()
app.include_router(router)


def override_get_db():
    """Provide a mock database session for router tests."""
    db = MagicMock()
    yield db


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


VALID_UNIT_OF_MEASURE = next(iter(UnitOfMeasure)).value
VALID_ALLERGEN = next(iter(CafeAllergen)).value


def valid_ingredient_payload():
    """Return a valid ingredient request body."""
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
    """Return data expected from the mocked repository."""
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


def test_create_ingredient_success(monkeypatch):
    """Test that a valid ingredient is successfully created."""
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


def test_create_ingredient_vendor_not_found(monkeypatch):
    """Test that a missing vendor returns HTTP 404."""
    mock_create = MagicMock(
        side_effect=VendorNotFoundError(999),
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


def test_create_ingredient_already_exists(monkeypatch):
    """Test that a duplicate ingredient returns HTTP 409."""
    mock_create = MagicMock(
        side_effect=IngredientAlreadyExistsError("Flour"),
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


def test_create_ingredient_constraint_error(monkeypatch):
    """Test that a constraint violation returns HTTP 409."""
    mock_create = MagicMock(
        side_effect=IngredientConstraintError(
            "ck_ingredient_unit_amount_positive",
        ),
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


def test_create_ingredient_database_error(monkeypatch):
    """Test that an unexpected SQLAlchemy error returns HTTP 500."""
    mock_create = MagicMock(
        side_effect=SQLAlchemyError("Database connection failed"),
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
    assert data["detail"]["message"] == (
        "An unexpected database error occurred "
        "while creating the ingredient."
    )


def test_create_ingredient_invalid_vendor_id():
    """Test that vendor_id must be greater than zero."""
    payload = valid_ingredient_payload()
    payload["vendor_id"] = 0

    response = client.post(
        "/ingredients/",
        json=payload,
    )

    assert response.status_code == 422


def test_create_ingredient_negative_purchasing_cost():
    """Test that purchasing_cost cannot be negative."""
    payload = valid_ingredient_payload()
    payload["purchasing_cost"] = "-5.00"

    response = client.post(
        "/ingredients/",
        json=payload,
    )

    assert response.status_code == 422


def test_create_ingredient_zero_unit_amount():
    """Test that unit_amount must be greater than zero."""
    payload = valid_ingredient_payload()
    payload["unit_amount"] = "0"

    response = client.post(
        "/ingredients/",
        json=payload,
    )

    assert response.status_code == 422


def test_create_ingredient_missing_name():
    """Test that name is required."""
    payload = valid_ingredient_payload()
    del payload["name"]

    response = client.post(
        "/ingredients/",
        json=payload,
    )

    assert response.status_code == 422


def test_create_ingredient_empty_name():
    """Test that ingredient name cannot be empty."""
    payload = valid_ingredient_payload()
    payload["name"] = ""

    response = client.post(
        "/ingredients/",
        json=payload,
    )

    assert response.status_code == 422


def test_read_all_ingredients_returns_200(monkeypatch):
    """Test that reading all ingredients returns HTTP 200."""
    monkeypatch.setattr(
        ingredient_router,
        "get_all_ingredients",
        lambda db: [],
    )

    response = client.get("/ingredients/all")

    assert response.status_code == 200


def test_read_all_ingredients_returns_empty_list(monkeypatch):
    """Test that no ingredients returns an empty list."""
    monkeypatch.setattr(
        ingredient_router,
        "get_all_ingredients",
        lambda db: [],
    )

    response = client.get("/ingredients/all")

    assert response.status_code == 200
    assert response.json()["ingredients"] == []


def test_read_all_ingredients_returns_ingredients(monkeypatch):
    """Test that all ingredients are returned successfully."""
    ingredients = [
        {
            "id": 1,
            "name": "Flour",
            "active": True,
            "purchasing_cost": 10.00,
            "unit_amount": 25.00,
            "unit_of_measure": VALID_UNIT_OF_MEASURE,
            "allergens": [
                {"name": VALID_ALLERGEN},
            ],
            "vendor_id": 1,
        },
    ]

    monkeypatch.setattr(
        ingredient_router,
        "get_all_ingredients",
        lambda db: ingredients,
    )

    response = client.get("/ingredients/all")

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == (
        "These are all the ingredients in your inventory!"
    )
    assert len(data["ingredients"]) == 1
    assert data["ingredients"][0]["name"] == "Flour"


def test_read_ingredient_returns_ingredient(monkeypatch):
    """Test that a valid ingredient ID returns the ingredient."""
    ingredient = valid_ingredient_response()

    mock_get = MagicMock(return_value=ingredient)

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


def test_read_ingredient_not_found(monkeypatch):
    """Test that a nonexistent ingredient ID returns HTTP 404."""
    mock_get = MagicMock(return_value=None)

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


def test_read_ingredient_invalid_id():
    """Test that a non-integer ingredient ID returns HTTP 422."""
    response = client.get("/ingredients/abc")

    assert response.status_code == 422


def test_read_all_ingredients_integration():
    """Test the complete GET /ingredients/all request flow.

    This test uses a real in-memory SQLite database and exercises
    the FastAPI router, repository, database query, and response.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(bind=engine)

    testing_session_local = sessionmaker(bind=engine)

    def override_real_db():
        """Provide a real test database session."""
        db = testing_session_local()

        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_real_db

    db = None

    try:
        db = testing_session_local()

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

        test_client = TestClient(app)

        response = test_client.get("/ingredients/all")

        assert response.status_code == 200

        data = response.json()

        assert data["message"] == (
            "These are all the ingredients in your inventory!"
        )
        assert len(data["ingredients"]) == 1
        assert data["ingredients"][0]["name"] == "Integration Flour"

    finally:
        app.dependency_overrides.clear()

        if db is not None:
            db.close()

        Base.metadata.drop_all(bind=engine)
        engine.dispose()