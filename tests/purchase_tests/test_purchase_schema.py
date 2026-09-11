from datetime import UTC, datetime

from purchase.purchase_schema import PurchaseItemSchema, PurchaseSchema


def test_purchase_item_schema_persistence(db):
    """PurchaseItemSchema should persist and retrieve correctly."""
    item = PurchaseItemSchema(
        purchase_id=1,
        item_type="baked_good",
        item_id=10,
        quantity=2,
        price_at_sale=4.50,
    )

    db.add(item)
    db.commit()
    db.refresh(item)

    assert item.id > 0
    assert item.purchase_id == 1
    assert item.item_type == "baked_good"
    assert item.item_id == 10
    assert item.quantity == 2
    assert item.price_at_sale == 4.50


def test_purchase_schema_defaults(db):
    """PurchaseSchema should set default created_at and loyalty_points_awarded."""
    purchase = PurchaseSchema(
        subtotal=10.00,
        discount_amount=2.00,
        tax_amount=0.56,
        total=8.56,
        customer_id=None,
        promo_id=None,
    )

    # BEFORE commit: SQLAlchemy has NOT applied column defaults yet
    assert purchase.created_at is None

    db.add(purchase)
    db.commit()
    db.refresh(purchase)

    # AFTER commit: default is applied, but SQLite strips timezone info
    assert isinstance(purchase.created_at, datetime)
    assert purchase.created_at.tzinfo is None

    assert purchase.id > 0
    assert purchase.subtotal == 10.00
    assert purchase.discount_amount == 2.00
    assert purchase.tax_amount == 0.56
    assert purchase.total == 8.56
    assert purchase.loyalty_points_awarded == 0


def test_purchase_schema_relationship_items(db):
    """PurchaseSchema.items should correctly map related PurchaseItemSchema rows."""
    purchase = PurchaseSchema(
        subtotal=20.00,
        discount_amount=0.00,
        tax_amount=1.40,
        total=21.40,
        customer_id=None,
        promo_id=None,
    )

    db.add(purchase)
    db.commit()
    db.refresh(purchase)

    item1 = PurchaseItemSchema(
        purchase_id=purchase.id,
        item_type="drink_recipe",
        item_id=3,
        quantity=1,
        price_at_sale=10.70,
    )

    item2 = PurchaseItemSchema(
        purchase_id=purchase.id,
        item_type="baked_good",
        item_id=7,
        quantity=2,
        price_at_sale=5.00,
    )

    db.add(item1)
    db.add(item2)
    db.commit()

    db.refresh(purchase)

    assert len(purchase.items) == 2
    assert purchase.items[0].purchase_id == purchase.id
    assert purchase.items[1].purchase_id == purchase.id


def test_purchase_schema_foreign_keys_nullable(db):
    """customer_id and promo_id should allow NULL values."""
    purchase = PurchaseSchema(
        subtotal=15.00,
        discount_amount=0.00,
        tax_amount=1.05,
        total=16.05,
        customer_id=None,
        promo_id=None,
    )

    db.add(purchase)
    db.commit()
    db.refresh(purchase)

    assert purchase.customer_id is None
    assert purchase.promo_id is None
