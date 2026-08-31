import models

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


from baked_good.baked_good_model import BakedGood, BakedGoodUpdate
from repositories.baked_good_repository import BakedGoodRepository
from database import Base
from exceptions.baked_good_exceptions import (
    BakedGoodNotFoundError,
    DuplicateBakedGoodError,
    VendorNotFoundError,
)
from vendor.vendor_schema import Vendor

TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=test_engine
)  # pylint: disable=invalid-name


@pytest.fixture
def db():
    """Creates a fresh database session for each test."""
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


def make_vendor(vendor_id=1, name="Test Vendor", email="vendor1@example.com"):
    """Creates and returns a Vendor object (not yet added to a session)."""
    return Vendor(
        id=vendor_id,
        active=True,
        name=name,
        contact_name="John Doe",
        contact_role="Manager",
        email=email,
        phone="555-123-4567",
    )


def test_create_baked_good_repository(db):
    vendor = make_vendor()
    db.add(vendor)
    db.commit()
    db.refresh(vendor)

    repository = BakedGoodRepository(db)

    baked_good = BakedGood(
        active=True,
        name="Chocolate Cake",
        description="A chocolate cake",
        purchasing_cost=5.00,
        retail_price=10.00,
        vendor_id=1,
    )

    created = repository.create_baked_good(baked_good)

    assert created.id is not None
    assert created.name == "Chocolate Cake"


def test_create_baked_good_returns_baked_good(db):
    vendor = make_vendor()
    db.add(vendor)
    db.commit()
    db.refresh(vendor)
    repository = BakedGoodRepository(db)

    baked_good = BakedGood(
        active=True,
        name="Chocolate Cake",
        description="A chocolate cake",
        purchasing_cost=5.00,
        retail_price=10.00,
        vendor_id=vendor.id,
    )

    result = repository.create_baked_good(baked_good)

    assert result.name == baked_good.name
    assert result.description == baked_good.description
    assert result.purchasing_cost == baked_good.purchasing_cost
    assert result.retail_price == baked_good.retail_price
    assert result.vendor_id == baked_good.vendor_id
    assert result.active == baked_good.active


def test_create_baked_good_invalid_vendor(db):
    repository = BakedGoodRepository(db)

    baked_good = BakedGood(
        active=True,
        name="Chocolate Cake",
        description="A chocolate cake",
        purchasing_cost=5.00,
        retail_price=10.00,
        vendor_id=9999,
    )

    with pytest.raises(
        VendorNotFoundError,
        match=f"Vendor with ID {baked_good.vendor_id} was not found."
    ):
        repository.create_baked_good(baked_good)


def test_create_baked_good_duplicate_name_raises(db):
    """
    Tests that creating a baked good with a name that differs only in
    case/whitespace from an existing baked good raises
    DuplicateBakedGoodError.
    """
    vendor = make_vendor()
    db.add(vendor)
    db.commit()
    db.refresh(vendor)

    repository = BakedGoodRepository(db)

    repository.create_baked_good(
        BakedGood(
            active=True,
            name="Blueberry Muffin",
            description="A fresh blueberry muffin",
            purchasing_cost=2.0,
            retail_price=4.0,
            vendor_id=vendor.id,
        )
    )

    with pytest.raises(DuplicateBakedGoodError):
        repository.create_baked_good(
            BakedGood(
                active=True,
                name="blueberry  muffin",
                description="Another muffin",
                purchasing_cost=2.0,
                retail_price=4.0,
                vendor_id=vendor.id,
            )
        )


def test_create_baked_good_same_name_different_vendor_currently_blocked(db):
    vendor_one = make_vendor(vendor_id=1, name="Vendor One", email="one@example.com")
    vendor_two = make_vendor(vendor_id=2, name="Vendor Two", email="two@example.com")
    db.add_all([vendor_one, vendor_two])
    db.commit()

    repository = BakedGoodRepository(db)

    repository.create_baked_good(
        BakedGood(
            active=True,
            name="Blueberry Muffin",
            description="A fresh blueberry muffin",
            purchasing_cost=2.0,
            retail_price=4.0,
            vendor_id=vendor_one.id,
        )
    )

    with pytest.raises(DuplicateBakedGoodError):
        repository.create_baked_good(
            BakedGood(
                active=True,
                name="Blueberry Muffin",
                description="A fresh blueberry muffin",
                purchasing_cost=2.0,
                retail_price=4.0,
                vendor_id=vendor_two.id,
            )
        )


def test_get_all_baked_goods_returns_empty_list(db):
    repository = BakedGoodRepository(db)

    assert repository.get_all_baked_goods() == []


def test_get_all_baked_goods_returns_all(db):
    vendor = make_vendor()
    db.add(vendor)
    db.commit()
    db.refresh(vendor)

    repository = BakedGoodRepository(db)

    repository.create_baked_good(
        BakedGood(
            active=True,
            name="Chocolate Cake",
            description="A chocolate cake",
            purchasing_cost=5.0,
            retail_price=10.0,
            vendor_id=vendor.id,
        )
    )
    repository.create_baked_good(
        BakedGood(
            active=True,
            name="Sourdough Loaf",
            description="A tangy sourdough loaf",
            purchasing_cost=3.0,
            retail_price=7.0,
            vendor_id=vendor.id,
        )
    )

    results = repository.get_all_baked_goods()

    assert len(results) == 2
    names = {item.name for item in results}
    assert names == {"Chocolate Cake", "Sourdough Loaf"}


def test_get_baked_good_by_id_found(db):
    vendor = make_vendor()
    db.add(vendor)
    db.commit()
    db.refresh(vendor)

    repository = BakedGoodRepository(db)
    created = repository.create_baked_good(
        BakedGood(
            active=True,
            name="Chocolate Cake",
            description="A chocolate cake",
            purchasing_cost=5.0,
            retail_price=10.0,
            vendor_id=vendor.id,
        )
    )

    found = repository.get_baked_good_by_id(created.id)

    assert found is not None
    assert found.id == created.id
    assert found.name == "Chocolate Cake"


def test_get_baked_good_by_id_returns_none_when_not_found(db):
    repository = BakedGoodRepository(db)

    assert repository.get_baked_good_by_id(9999) is None


# --- update_baked_good ---


def test_update_baked_good_success(db):
    vendor = make_vendor()
    db.add(vendor)
    db.commit()
    db.refresh(vendor)

    repository = BakedGoodRepository(db)
    created = repository.create_baked_good(
        BakedGood(
            active=True,
            name="Chocolate Cake",
            description="A chocolate cake",
            purchasing_cost=5.0,
            retail_price=10.0,
            vendor_id=vendor.id,
        )
    )

    update_data = BakedGoodUpdate(
        active=False,
        name="Double Chocolate Cake",
        description="An even richer chocolate cake",
        purchasing_cost=6.0,
        retail_price=12.0,
        vendor_id=vendor.id,
    )

    updated = repository.update_baked_good(created.id, update_data)

    assert updated.id == created.id
    assert updated.active is False
    assert updated.name == "Double Chocolate Cake"
    assert updated.description == "An even richer chocolate cake"
    assert updated.purchasing_cost == 6.0
    assert updated.retail_price == 12.0


def test_update_baked_good_persists_to_database(db):
    vendor = make_vendor()
    db.add(vendor)
    db.commit()
    db.refresh(vendor)

    repository = BakedGoodRepository(db)
    created = repository.create_baked_good(
        BakedGood(
            active=True,
            name="Bagel",
            description="A plain bagel",
            purchasing_cost=1.0,
            retail_price=2.5,
            vendor_id=vendor.id,
        )
    )

    update_data = BakedGoodUpdate(
        active=True,
        name="Everything Bagel",
        description="A bagel with everything seasoning",
        purchasing_cost=1.25,
        retail_price=3.0,
        vendor_id=vendor.id,
    )

    repository.update_baked_good(created.id, update_data)

    persisted = repository.get_baked_good_by_id(created.id)

    assert persisted.name == "Everything Bagel"
    assert persisted.retail_price == 3.0


def test_update_baked_good_raises_when_id_not_found(db):
    vendor = make_vendor()
    db.add(vendor)
    db.commit()
    db.refresh(vendor)

    repository = BakedGoodRepository(db)

    update_data = BakedGoodUpdate(
        active=True,
        name="Ghost Pastry",
        description="Does not exist",
        purchasing_cost=1.0,
        retail_price=2.0,
        vendor_id=vendor.id,
    )

    with pytest.raises(
        BakedGoodNotFoundError,
        match="Baked good with ID 9999 was not found."
    ):
        repository.update_baked_good(9999, update_data)


def test_update_baked_good_raises_when_vendor_not_found(db):
    vendor = make_vendor()
    db.add(vendor)
    db.commit()
    db.refresh(vendor)

    repository = BakedGoodRepository(db)
    created = repository.create_baked_good(
        BakedGood(
            active=True,
            name="Croissant",
            description="A buttery croissant",
            purchasing_cost=1.5,
            retail_price=3.5,
            vendor_id=vendor.id,
        )
    )

    update_data = BakedGoodUpdate(
        active=True,
        name="Croissant",
        description="A buttery croissant",
        purchasing_cost=1.5,
        retail_price=3.5,
        vendor_id=9999,
    )

    with pytest.raises(VendorNotFoundError):
        repository.update_baked_good(created.id, update_data)


def test_update_baked_good_allows_keeping_own_name(db):
    vendor = make_vendor()
    db.add(vendor)
    db.commit()
    db.refresh(vendor)

    repository = BakedGoodRepository(db)
    created = repository.create_baked_good(
        BakedGood(
            active=True,
            name="Cinnamon Roll",
            description="A gooey cinnamon roll",
            purchasing_cost=2.0,
            retail_price=4.5,
            vendor_id=vendor.id,
        )
    )

    update_data = BakedGoodUpdate(
        active=True,
        name="Cinnamon Roll",
        description="An even gooier cinnamon roll",
        purchasing_cost=2.25,
        retail_price=5.0,
        vendor_id=vendor.id,
    )

    updated = repository.update_baked_good(created.id, update_data)

    assert updated.name == "Cinnamon Roll"
    assert updated.description == "An even gooier cinnamon roll"


def test_update_baked_good_raises_when_name_belongs_to_another_baked_good(db):
    vendor = make_vendor()
    db.add(vendor)
    db.commit()
    db.refresh(vendor)

    repository = BakedGoodRepository(db)

    repository.create_baked_good(
        BakedGood(
            active=True,
            name="Blueberry Muffin",
            description="A fresh blueberry muffin",
            purchasing_cost=2.0,
            retail_price=4.0,
            vendor_id=vendor.id,
        )
    )

    second = repository.create_baked_good(
        BakedGood(
            active=True,
            name="Banana Bread",
            description="A moist banana bread",
            purchasing_cost=2.0,
            retail_price=4.5,
            vendor_id=vendor.id,
        )
    )

    update_data = BakedGoodUpdate(
        active=True,
        name="Blueberry Muffin",
        description="A moist banana bread",
        purchasing_cost=2.0,
        retail_price=4.5,
        vendor_id=vendor.id,
    )

    with pytest.raises(DuplicateBakedGoodError):
        repository.update_baked_good(second.id, update_data)


def test_update_baked_good_reassigns_vendor_relationship(db):
    vendor_one = make_vendor(vendor_id=1, name="Vendor One", email="one@example.com")
    vendor_two = make_vendor(vendor_id=2, name="Vendor Two", email="two@example.com")
    db.add_all([vendor_one, vendor_two])
    db.commit()
    db.refresh(vendor_one)
    db.refresh(vendor_two)

    repository = BakedGoodRepository(db)
    created = repository.create_baked_good(
        BakedGood(
            active=True,
            name="Baguette",
            description="A crusty baguette",
            purchasing_cost=1.0,
            retail_price=3.0,
            vendor_id=vendor_one.id,
        )
    )

    update_data = BakedGoodUpdate(
        active=True,
        name="Baguette",
        description="A crusty baguette",
        purchasing_cost=1.0,
        retail_price=3.0,
        vendor_id=vendor_two.id,
    )

    updated = repository.update_baked_good(created.id, update_data)

    assert updated.vendor_id == vendor_two.id
    assert updated.vendor.id == vendor_two.id

    db.refresh(vendor_one)
    db.refresh(vendor_two)

    # Assumes Vendor.baked_good is the list-side of the relationship,
    # per BakedGoodSchema's back_populates="baked_good". Adjust the
    # attribute name here if Vendor's actual relationship is named
    # differently.
    assert updated in vendor_two.baked_good
    assert updated not in vendor_one.baked_good
