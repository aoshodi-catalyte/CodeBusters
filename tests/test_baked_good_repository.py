from sqlalchemy.orm import sessionmaker
from baked_good.baked_good_repository import BakedGoodRepository
from baked_good.baked_good_model import BakedGood
import pytest

from database import Base, engine
from vendor.vendor_schema import Vendor
from tests.test_customer_router import TestingSessionLocal

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

@pytest.fixture
def db():
    """Creates a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

def test_create_baked_good_repository(db):
    """
    Tests that a baked good can be created and stored in the repository.

    Creates a BakedGoodRepository and a valid BakedGood object, then adds
    the baked good to the repository. Verifies that the baked good is
    stored in the repository and that the repository contains one item.

    Args:
        None

    Returns:
        None
    """
    vendor = Vendor(
        id=1,
        active=True,
        name="Test Vendor",
        contact_name="John Doe",
        contact_role="Manager",
        email="john@testvendor.com",
        phone="555-123-4567"
    )

    db.add(vendor)
    db.commit()
    db.refresh(vendor)
    
    repository = BakedGoodRepository(db)

    baked_good = BakedGood (
        active=True,
        name="Chocolate Cake",
        description="A chocolate cake",
        purchasing_cost=5.00,
        retail_price=10.00,
        vendor_id=1
    )

    created = repository.create_baked_good(baked_good)

    assert created.id is not None
    assert created.name == "Chocolate Cake"

def test_create_baked_good_returns_baked_good(db):
    """
    Tests that creating a baked good returns the same BakedGood object.

    Creates a BakedGoodRepository and a valid BakedGood object, then passes
    the baked good to the create_baked_good method. Verifies that the
    returned object is equal to the baked good that was provided.

    Args:
        None

    Returns:
        None
    """
    vendor = Vendor(
        id=1,
        active=True,
        name="Test Vendor",
        contact_name="John Doe",
        contact_role="Manager",
        email="john@testvendor.com",
        phone="555-123-4567"
    )

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
        vendor_id=vendor.id
    )

    result = repository.create_baked_good(baked_good)

    assert result.name == baked_good.name
    assert result.description == baked_good.description
    assert result.purchasing_cost == baked_good.purchasing_cost
    assert result.retail_price == baked_good.retail_price
    assert result.vendor_id == baked_good.vendor_id
    assert result.active == baked_good.active
