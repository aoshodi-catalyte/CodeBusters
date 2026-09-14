from datetime import UTC, datetime, timedelta

import pytest

from baked_good.baked_good_schema import BakedGoodSchema
from customer.customer_schema import CustomerSchema
from drink_recipe.drink_recipe_schema import DrinkRecipeSchema
from promotion.promotion_schema import PromotionSchema


def create_baked_good(db, price=4.00):
    item = BakedGoodSchema(
        active=True,
        name="Chocolate Cake",
        description="A chocolate cake",
        purchasing_cost=10.0,
        retail_price=price,
        vendor_id = 1
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def create_drink_recipe(db, price=4.00):
    item = DrinkRecipeSchema(
        name="latte",
        description="drink",
        active=True,
        type_id=1,
        sale_price=price
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def create_customer(db, points=0):
    cust = CustomerSchema(
        first_name="Jhon",
        last_name="Doe",
        active=True,
        email="jdoe@gmail.com",
        phone_number=7732029365,
        loyalty_points=points
    )
    db.add(cust)
    db.commit()
    db.refresh(cust)
    return cust


def create_promo(db, pct=20, active=True, valid=True):
    now = datetime.now(UTC)
    promo = PromotionSchema(
        promo_code="20OFF",
        discount_percentage=pct,
        active=active,
        start_datetime=now - timedelta(days=1) if valid else now + timedelta(days=1),
        end_datetime=now + timedelta(days=1) if valid else now - timedelta(days=1),
    )
    db.add(promo)
    db.commit()
    db.refresh(promo)
    return promo


def test_create_purchase(client, db):
    item = create_baked_good(db, price=5.00)

    payload = {
        "customer_id": None,
        "promo_id": None,
        "items": [
            {"item_type": "baked_good", "item_id": item.id, "quantity": 2}
        ],
    }

    response = client.post("/purchases", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert data["subtotal"] == 10.00
    assert data["discount_amount"] == 0.00
    assert data["tax_amount"] == 0.70
    assert data["total"] == 10.70
    assert data["loyalty_points_awarded"] == 10
    assert len(data["items"]) == 1


def test_create_purchase_with_promo(client, db):
    item = create_baked_good(db, price=10.00)
    promo = create_promo(db, pct=20)

    payload = {
        "customer_id": None,
        "promo_id": promo.id,
        "items": [
            {"item_type": "baked_good", "item_id": item.id, "quantity": 1}
        ],
    }

    response = client.post("/purchases", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert data["subtotal"] == 10.00
    assert data["discount_amount"] == 2.00
    assert data["total"] == 8.56


def test_get_purchase_by_id(client, db):
    item = create_baked_good(db, price=5.00)

    payload = {
        "customer_id": None,
        "promo_id": None,
        "items": [
            {"item_type": "baked_good", "item_id": item.id, "quantity": 1}
        ],
    }

    created = client.post("/purchases", json=payload).json()
    purchase_id = created["id"]

    response = client.get(f"/purchases/{purchase_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == purchase_id
    assert data["subtotal"] == 5.00


def test_get_purchase_not_found(client):
    response = client.get("/purchases/999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_list_purchases(client, db):
    item = create_drink_recipe(db, price=4.00)

    payload1 = {
        "customer_id": None,
        "promo_id": None,
        "items": [
            {"item_type": "drink_recipe", "item_id": item.id, "quantity": 1}
        ],
    }

    payload2 = {
        "customer_id": None,
        "promo_id": None,
        "items": [
            {"item_type": "drink_recipe", "item_id": item.id, "quantity": 2}
        ],
    }

    client.post("/purchases", json=payload1)
    client.post("/purchases", json=payload2)

    response = client.get("/purchases")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 2
    totals = {d["total"] for d in data}
    assert totals == {4.28, 8.56}
