from datetime import UTC, datetime, timedelta

import pytest

from baked_good.baked_good_schema import BakedGoodSchema
from drink_recipe.drink_recipe_schema import DrinkRecipeSchema
from promotion.promotion_schema import PromotionSchema
from purchase.purchase_schema import PurchaseSchema
from repositories.purchase_repository import PurchaseRepository


@pytest.fixture
def repo(db):
    return PurchaseRepository(db)


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


def test_get_item_price_baked_good(repo, db):
    item = create_baked_good(db, price=7.50)
    price = repo.get_item_price("baked_good", item.id)
    assert price == 7.50


def test_get_item_price_drink_recipe(repo, db):
    item = create_drink_recipe(db, price=3.25)
    price = repo.get_item_price("drink_recipe", item.id)
    assert price == 3.25


def test_get_item_price_invalid_type(repo):
    with pytest.raises(ValueError):
        repo.get_item_price("invalid_type", 1)


def test_get_item_price_missing_item(repo):
    with pytest.raises(ValueError):
        repo.get_item_price("baked_good", 999)


def test_get_promotion_found(repo, db):
    promo = create_promo(db)
    result = repo.get_promotion(promo.id)
    assert result.id == promo.id


def test_get_promotion_not_found(repo):
    assert repo.get_promotion(999) is None


def test_create_purchase_persists_purchase_and_items(repo, db):
    baked = create_baked_good(db, price=5.00)
    drink = create_drink_recipe(db, price=4.00)

    purchase_data = {
        "subtotal": 13.00,
        "discount_amount": 0.00,
        "tax_amount": 0.91,
        "total": 13.91,
        "loyalty_points_awarded": 13,
        "customer_id": None,
        "promo_id": None,
    }

    items = [
        {
            "item_type": "baked_good",
            "item_id": baked.id,
            "quantity": 1,
            "price_at_sale": 5.00,
        },
        {
            "item_type": "drink_recipe",
            "item_id": drink.id,
            "quantity": 2,
            "price_at_sale": 4.00,
        },
    ]

    purchase = repo.create_purchase(purchase_data, items)

    assert purchase.id > 0
    assert purchase.total == 13.91
    assert len(purchase.items) == 2

    # Validate item fields
    assert purchase.items[0].item_type == "baked_good"
    assert purchase.items[1].item_type == "drink_recipe"


def test_get_purchase_found(repo, db):
    purchase = PurchaseSchema(
        subtotal=10.00,
        discount_amount=0.00,
        tax_amount=0.70,
        total=10.70,
        loyalty_points_awarded=10,
        customer_id=None,
        promo_id=None,
    )
    db.add(purchase)
    db.commit()
    db.refresh(purchase)

    result = repo.get_purchase(purchase.id)
    assert result.id == purchase.id


def test_get_purchase_not_found(repo):
    assert repo.get_purchase(999) is None


def test_list_purchases(repo, db):
    p1 = PurchaseSchema(
        subtotal=10.00,
        discount_amount=0.00,
        tax_amount=0.70,
        total=10.70,
        loyalty_points_awarded=10,
        customer_id=None,
        promo_id=None,
    )
    p2 = PurchaseSchema(
        subtotal=20.00,
        discount_amount=0.00,
        tax_amount=1.40,
        total=21.40,
        loyalty_points_awarded=21,
        customer_id=None,
        promo_id=None,
    )

    db.add(p1)
    db.add(p2)
    db.commit()

    results = repo.list_purchases()
    assert len(results) == 2
    assert results[0].total in (10.70, 21.40)
    assert results[1].total in (10.70, 21.40)
