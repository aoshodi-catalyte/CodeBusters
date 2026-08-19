"""Tests for the ingredient API router."""

from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from constants.INGREDIENT_TYPES import CafeAllergen, UnitOfMeasure
from database import get_db
from ingredient.ingredient_exceptions import (
    IngredientAlreadyExistsError,
    IngredientConstraintError,
    VendorNotFoundError,
)
from ingredient.ingredient_router import router
import ingredient.ingredient_router as ingredient_router


# ============================================================
# TEST APPLICATION
# ============================================================

app = FastAPI()
app.include_router(router)


def override_get_db():
    """Provide a mock database session for router tests."""
    db = MagicMock()
    yield db


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


# ============================================================
# TEST DATA
# ============================================================

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
    """Return the data that the mocked repository would return."""
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
# SUCCESSFUL CREATION
# ============================================================

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


# ============================================================
# VENDOR DOES NOT EXIST
# ============================================================

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


# ============================================================
# DUPLICATE INGREDIENT
# ============================================================

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


# ============================================================
# DATABASE CONSTRAINT ERROR
# ============================================================

def test_create_ingredient_constraint_error(monkeypatch):
    """Test that a database constraint violation returns HTTP 409."""
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


# ============================================================
# UNEXPECTED DATABASE ERROR
# ============================================================

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
    assert (
        data["detail"]["message"]
        == "An unexpected database error occurred "
        "while creating the ingredient."
    )


# ============================================================
# INVALID VENDOR ID
# ============================================================

def test_create_ingredient_invalid_vendor_id():
    """Test that vendor_id must be greater than zero."""
    payload = valid_ingredient_payload()
    payload["vendor_id"] = 0

    response = client.post(
        "/ingredients/",
        json=payload,
    )

    assert response.status_code == 422


# ============================================================
# NEGATIVE PURCHASING COST
# ============================================================

def test_create_ingredient_negative_purchasing_cost():
    """Test that purchasing_cost cannot be negative."""
    payload = valid_ingredient_payload()
    payload["purchasing_cost"] = "-5.00"

    response = client.post(
        "/ingredients/",
        json=payload,
    )

    assert response.status_code == 422


# ============================================================
# ZERO UNIT AMOUNT
# ============================================================

def test_create_ingredient_zero_unit_amount():
    """Test that unit_amount must be greater than zero."""
    payload = valid_ingredient_payload()
    payload["unit_amount"] = "0"

    response = client.post(
        "/ingredients/",
        json=payload,
    )

    assert response.status_code == 422


# ============================================================
# MISSING REQUIRED FIELD
# ============================================================

def test_create_ingredient_missing_name():
    """Test that name is required."""
    payload = valid_ingredient_payload()
    del payload["name"]

    response = client.post(
        "/ingredients/",
        json=payload,
    )

    assert response.status_code == 422


# ============================================================
# EMPTY INGREDIENT NAME
# ============================================================

def test_create_ingredient_empty_name():
    """Test that ingredient name cannot be empty."""
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