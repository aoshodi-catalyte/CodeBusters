import pytest
from datetime import datetime, UTC
from decimal import Decimal

from purchase.purchase_model import (
    PurchaseItemCreate,
    PurchaseCreate,
    PurchaseItemResponse,
    PurchaseResponse,
)


def test_purchase_item_create_valid():
    item = PurchaseItemCreate(
        item_type="baked_good",
        item_id=1,
        quantity=2
    )

    assert item.item_type == "baked_good"
    assert item.item_id == 1
    assert item.quantity == 2


def test_purchase_item_create_invalid_item_type():
    with pytest.raises(ValueError):
        PurchaseItemCreate(item_type="", item_id=1, quantity=1)


def test_purchase_item_create_invalid_item_id():
    with pytest.raises(ValueError):
        PurchaseItemCreate(item_type="drink_recipe", item_id=0, quantity=1)


def test_purchase_item_create_invalid_quantity():
    with pytest.raises(ValueError):
        PurchaseItemCreate(item_type="drink_recipe", item_id=1, quantity=0)


def test_purchase_create_valid():
    payload = PurchaseCreate(
        customer_id=10,
        promo_id=5,
        items=[
            PurchaseItemCreate(item_type="baked_good", item_id=1, quantity=2)
        ]
    )

    assert payload.customer_id == 10
    assert payload.promo_id == 5
    assert len(payload.items) == 1


def test_purchase_create_requires_items():
    with pytest.raises(ValueError):
        PurchaseCreate(items=[])


def test_purchase_item_response_valid():
    item = PurchaseItemResponse(
        id=1,
        item_type="baked_good",
        item_id=2,
        quantity=3,
        price_at_sale=Decimal("4.50")
    )

    assert item.id == 1
    assert item.item_type == "baked good"
    assert item.item_id == 2
    assert item.quantity == 3
    assert item.price_at_sale == Decimal("4.50")


def test_purchase_item_response_from_attributes():
    class FakeItem:
        id = 99
        item_type = "drink_recipe"
        item_id = 7
        quantity = 1
        price_at_sale = Decimal("2.75")

    item = PurchaseItemResponse.model_validate(FakeItem(), from_attributes=True)

    assert item.id == 99
    assert item.item_type == "drink"
    assert item.item_id == 7
    assert item.quantity == 1
    assert item.price_at_sale == Decimal("2.75")


def test_purchase_response_valid():
    now = datetime.now(UTC)

    response = PurchaseResponse(
        id=1,
        customer_id=10,
        promo_id=5,
        subtotal=Decimal("10.00"),
        discount_amount=Decimal("2.00"),
        tax_amount=Decimal("0.56"),
        total=Decimal("8.56"),
        loyalty_points_awarded=8,
        created_at=now,
        items=[
            PurchaseItemResponse(
                id=1,
                item_type="baked_good",
                item_id=2,
                quantity=1,
                price_at_sale=Decimal("10.00")
            )
        ]
    )

    assert response.id == 1
    assert response.customer_id == 10
    assert response.promo_id == 5
    assert response.subtotal == Decimal("10.00")
    assert response.discount_amount == Decimal("2.00")
    assert response.tax_amount == Decimal("0.56")
    assert response.total == Decimal("8.56")
    assert response.loyalty_points_awarded == 8
    assert response.created_at == now
    assert len(response.items) == 1


def test_purchase_response_from_attributes():
    now = datetime.now(UTC)

    class FakePurchase:
        id = 42
        customer_id = None
        promo_id = None
        subtotal = Decimal("20.00")
        discount_amount = Decimal("0.00")
        tax_amount = Decimal("1.40")
        total = Decimal("21.40")
        loyalty_points_awarded = 21
        created_at = now
        items = [
            type("FakeItem", (), {
                "id": 1,
                "item_type": "drink_recipe",
                "item_id": 3,
                "quantity": 2,
                "price_at_sale": Decimal("10.70")
            })()
        ]

    response = PurchaseResponse.model_validate(FakePurchase(), from_attributes=True)

    assert response.id == 42
    assert response.total == Decimal("21.40")
    assert response.items[0].item_type == "drink"
