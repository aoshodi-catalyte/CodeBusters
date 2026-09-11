import pytest
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException

from baked_good.baked_good_schema import BakedGoodSchema
from customer.customer_schema import CustomerSchema
from drink_recipe.drink_recipe_schema import DrinkRecipeSchema
from promotion.promotion_schema import PromotionSchema
from purchase.purchase_model import PurchaseCreate, PurchaseItemCreate
from purchase.purchase_schema import PurchaseItemSchema, PurchaseSchema
from purchase.purchase_service_logic import PurchaseService


def create_baked_good(db):
    item = BakedGoodSchema(
        active=True,
        name="Chocolate Cake",
        description="A chocolate cake",
        purchasing_cost=10.0,
        retail_price=15.0,
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

def test_purchase_service_basic_purchase(db):
    """Subtotal, tax, total, loyalty points should compute correctly."""
    item = create_baked_good(db)
    payload = PurchaseCreate(
        customer_id=None,
        promo_id=None,
        items=[PurchaseItemCreate(item_type="baked_good", item_id=item.id, quantity=2)],
    )

    service = PurchaseService(db)
    purchase = service.create_purchase(payload)

    assert purchase.subtotal == 30.00
    assert purchase.discount_amount == 0.00
    assert purchase.tax_amount == 2.1
    assert purchase.total == 32.10
    assert purchase.loyalty_points_awarded == 32


def test_purchase_service_with_promotion(db):
    """Promotion should apply correct discount."""
    item = create_baked_good(db)
    promo = create_promo(db, pct=20)

    payload = PurchaseCreate(
        customer_id=None,
        promo_id=promo.id,
        items=[PurchaseItemCreate(item_type="baked_good", item_id=item.id, quantity=1)],
    )

    service = PurchaseService(db)
    purchase = service.create_purchase(payload)

    assert purchase.subtotal == 15.00
    assert purchase.discount_amount == 3.00
    assert purchase.tax_amount == 0.84
    assert purchase.total == 12.84
    assert purchase.loyalty_points_awarded == 12


def test_purchase_service_invalid_promo_id(db):
    """Invalid promo ID should raise 404."""
    item = create_baked_good(db)

    payload = PurchaseCreate(
        customer_id=None,
        promo_id=999,
        items=[PurchaseItemCreate(item_type="baked_good", item_id=item.id, quantity=1)],
    )

    service = PurchaseService(db)

    with pytest.raises(HTTPException) as exc:
        service.create_purchase(payload)

    assert exc.value.status_code == 404


def test_purchase_service_inactive_promo(db):
    """Inactive promo should raise 400."""
    item = create_baked_good(db)
    promo = create_promo(db, pct=20, active=False)

    payload = PurchaseCreate(
        customer_id=None,
        promo_id=promo.id,
        items=[PurchaseItemCreate(item_type="baked_good", item_id=item.id, quantity=1)],
    )

    service = PurchaseService(db)

    with pytest.raises(HTTPException) as exc:
        service.create_purchase(payload)

    assert exc.value.status_code == 400
    assert "not active" in exc.value.detail.lower()


def test_purchase_service_expired_promo(db):
    """Expired promo should raise 400."""
    item = create_baked_good(db)
    promo = create_promo(db, pct=20, valid=False)

    payload = PurchaseCreate(
        customer_id=None,
        promo_id=promo.id,
        items=[PurchaseItemCreate(item_type="baked_good", item_id=item.id, quantity=1)],
    )

    service = PurchaseService(db)

    with pytest.raises(HTTPException) as exc:
        service.create_purchase(payload)

    assert exc.value.status_code == 400
    assert "valid date range" in exc.value.detail.lower()


def test_purchase_service_customer_loyalty_update(db):
    """Customer loyalty points should increase based on total."""
    item = create_baked_good(db)
    customer = create_customer(db, points=10)

    payload = PurchaseCreate(
        customer_id=customer.id,
        promo_id=None,
        items=[PurchaseItemCreate(item_type="baked_good", item_id=item.id, quantity=2)],
    )

    service = PurchaseService(db)
    purchase = service.create_purchase(payload)

    db.refresh(customer)

    assert purchase.total == 32.1
    assert customer.loyalty_points == 42


def test_purchase_service_creates_line_items(db):
    """Line items should be persisted correctly."""
    item = create_drink_recipe(db)

    payload = PurchaseCreate(
        customer_id=None,
        promo_id=None,
        items=[PurchaseItemCreate(item_type="drink_recipe", item_id=item.id, quantity=3)],
    )

    service = PurchaseService(db)
    purchase = service.create_purchase(payload)

    assert len(purchase.items) == 1
    assert purchase.items[0].item_type == "drink_recipe"
    assert purchase.items[0].quantity == 3
    assert purchase.items[0].price_at_sale == 4.00
