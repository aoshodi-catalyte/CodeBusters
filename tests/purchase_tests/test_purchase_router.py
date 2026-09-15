from decimal import Decimal
import token

import pytest

from baked_good.baked_good_schema import BakedGoodSchema
from drink_recipe.drink_recipe_schema import DrinkRecipeSchema
from drink_recipe.drink_type_schema import DrinkTypeSchema
import models
from tests.factories.auth_factories import manager_token
from vendor.vendor_schema import Vendor


def create_vendor(db):
    """
    Creates a vendor directly in the test database.
    """
    vendor = Vendor(
        active=True,
        name="Test Vendor",
        contact_name="Test Contact",
        contact_role="Manager",
        email="vendor@example.com",
        phone="5555555555",
    )

    db.add(vendor)
    db.commit()
    db.refresh(vendor)

    return vendor


def create_baked_good(db, price=Decimal("4.00")):
    """
    Creates a baked good directly in the test database.
    """
    vendor = create_vendor(db)

    baked_good = BakedGoodSchema(
        name="Test Brownie",
        description="Test brownie",
        purchasing_cost=Decimal("2.00"),
        retail_price=price,
        active=True,
        vendor_id=vendor.id,
    )

    db.add(baked_good)
    db.commit()
    db.refresh(baked_good)

    return baked_good


def create_drink_type(db):
    """
    Creates a drink type directly in the test database.
    """
    drink_type = DrinkTypeSchema(
        name="Coffee",
        description="Coffee-based drinks",
    )

    db.add(drink_type)
    db.commit()
    db.refresh(drink_type)

    return drink_type


def create_drink(db, price=Decimal("4.00")):
    """
    Creates a drink recipe directly in the test database.
    """
    drink_type = create_drink_type(db)

    drink = DrinkRecipeSchema(
        name="Test Coffee",
        description="Test coffee",
        production_cost=Decimal("2.00"),
        sale_price=price,
        active=True,
        type_id=drink_type.id,
    )

    db.add(drink)
    db.commit()
    db.refresh(drink)

    return drink


# ---------------------------------------------------------------------------
# POST /purchases
# ---------------------------------------------------------------------------

def test_create_purchase_no_promo(client, db):
    """
    AC: A purchase can be created without a promotion.
    """

    baked_good = create_baked_good(
        db,
        Decimal("4.00"),
    )

    response = client.post(
        "/purchases",
        json={
            "items": [
                {
                    "item_type": "baked_good",
                    "item_id": baked_good.id,
                    "quantity": 1,
                }
            ]
        },
    )

def test_create_purchase(client, db):
    item = create_baked_good(db, price=5.00)
    token = manager_token()

    payload = {
        "customer_id": None,
        "employee_id": 1,
        "promo_id": None,
        "items": [
            {"item_type": "baked_good", "item_id": item.id, "quantity": 2}
        ],
    }

    response = client.post("/purchases", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 201

    data = response.json()
    assert data["subtotal"] == 10.00
    assert data["discount_amount"] == 0.00
    assert data["tax_amount"] == 0.70
    assert data["total"] == 10.70
    assert data["loyalty_points_awarded"] == 10
    assert data["employee_id"] == 1
    assert len(data["items"]) == 1


# ---------------------------------------------------------------------------
# GET /purchases/{purchase_id}
# ---------------------------------------------------------------------------

def test_get_purchase_by_id(client, db):
    """
    AC: A valid purchase ID returns the corresponding purchase.
    """

    baked_good = create_baked_good(
        db,
        Decimal("4.00"),
    )
    token = manager_token()

    create_response = client.post(
        "/purchases",
        json={
            "items": [
                {
                    "item_type": "baked_good",
                    "item_id": baked_good.id,
                    "quantity": 1,
                }
            ]
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    assert create_response.status_code == 201, create_response.json()

    purchase_id = create_response.json()["id"]

    response = client.get(
        f"/purchases/{purchase_id}"
    )

    assert response.status_code == 200, response.json()

    data = response.json()

    assert data["id"] == purchase_id
    assert data["subtotal"] == 4.00
    assert data["discount_amount"] == 0.00
    assert data["tax_amount"] == 0.28
    assert data["total"] == 4.28
    assert data["items"][0]["price_at_sale"] == 4.00


def test_get_purchase_not_found(client):
    """
    AC: An invalid purchase ID returns 404.
    """

    response = client.get("/purchases/999999")

    assert response.status_code == 404


# ---------------------------------------------------------------------------
# GET /purchases
# ---------------------------------------------------------------------------

def test_list_purchases(client, db):
    """
    AC: All purchases are returned when requesting the purchase list.
    """

    baked_good = create_baked_good(
        db,
        Decimal("4.00"),
    )
    token = manager_token()

    first_response = client.post(
        "/purchases",
        json={
            "items": [
                {
                    "item_type": "baked_good",
                    "item_id": baked_good.id,
                    "quantity": 1,
                }
            ]
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    assert first_response.status_code == 201, first_response.json()

    second_response = client.post(
        "/purchases",
        json={
            "items": [
                {
                    "item_type": "baked_good",
                    "item_id": baked_good.id,
                    "quantity": 2,
                }
            ]
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    assert second_response.status_code == 201, second_response.json()

    response = client.get("/purchases")

    assert response.status_code == 200, response.json()

    data = response.json()
    assert len(data) == 2
    totals = {d["total"] for d in data}
    assert totals == {4.28, 8.56}

def test_create_purchase_uses_employee_id_from_jwt(client, db):
    item = create_baked_good(db, price=5.00)
    token = manager_token()
    payload = {
        "customer_id": None,
        "promo_id": None,
        "employee_id": 999,
        "items": [
            {
                "item_type": "baked_good",
                "item_id": item.id,
                "quantity": 1,
            }
        ],
    }

    response = client.post("/purchases", json=payload, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 201

    data = response.json()

    assert data["employee_id"] == 1
    assert data["employee_id"] != 999

def test_create_purchase_customer_not_found(client, db):
    item = create_baked_good(db, price=5.00)
    token = manager_token()

    payload = {
        "customer_id": 999,
        "promo_id": None,
        "items": [
            {
                "item_type": "baked_good",
                "item_id": item.id,
                "quantity": 1,
            }
        ],
    }

    response = client.post("/purchases", json=payload, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 404
    assert "customer" in response.json()["detail"].lower()

def test_create_purchase_baked_good_not_found(client):
    token = manager_token()
    payload = {
        "customer_id": None,
        "promo_id": None,
        "items": [
            {
                "item_type": "baked_good",
                "item_id": 999,
                "quantity": 1,
            }
        ],
    }

    response = client.post("/purchases", json=payload, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 404
    assert "baked good" in response.json()["detail"].lower()

def test_create_purchase_drink_recipe_not_found(client):
    token = manager_token()
    payload = {
        "customer_id": None,
        "promo_id": None,
        "items": [
            {
                "item_type": "drink_recipe",
                "item_id": 999,
                "quantity": 1,
            }
        ],
    }

    response = client.post("/purchases", json=payload, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 404
    assert "drink recipe" in response.json()["detail"].lower()

def test_create_purchase_requires_at_least_one_item(client):
    token = manager_token()
    payload = {
        "customer_id": None,
        "promo_id": None,
        "items": [],
    }

    response = client.post("/purchases", json=payload, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 422

def test_create_purchase_rejects_invalid_quantity(client, db):
    item = create_baked_good(db)
    token = manager_token()
    payload = {
        "customer_id": None,
        "promo_id": None,
        "items": [
            {
                "item_type": "baked_good",
                "item_id": item.id,
                "quantity": 0,
            }
        ],
    }

    response = client.post("/purchases", json=payload, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 422
