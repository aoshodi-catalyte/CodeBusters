import models

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


from baked_good.baked_good_model import BakedGood
from repositories.baked_good_repository import BakedGoodRepository
from database import Base
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


def test_create_baked_good_repository(db):
    """
    Tests that a baked good can be created and stored in the repository.

    Creates a BakedGoodRepository and a valid BakedGood object, then
    creates the baked good through the repository. Verifies that the
    returned database object has a generated ID and contains the
    expected baked good data.

      Args:
        db: The SQLAlchemy database session used for the test.

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
        phone="555-123-4567",
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
        vendor_id=1,
    )

    created = repository.create_baked_good(baked_good)

    assert created.id is not None
    assert created.name == "Chocolate Cake"


def test_create_baked_good_returns_baked_good(db):
    """
    Tests that creating a baked good returns the expected database object.

    Creates a BakedGoodRepository and a valid BakedGood object, then
    creates the baked good through the repository. Verifies that the
    returned BakedGoodSchema contains the same data as the original
    BakedGood object.

    Args:
        db: The SQLAlchemy database session used for the test.

    Returns:
        None.
    """
    vendor = Vendor(
        id=1,
        active=True,
        name="Test Vendor",
        contact_name="John Doe",
        contact_role="Manager",
        email="john@testvendor.com",
        phone="555-123-4567",
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
    """
    Tests that a baked good cannot be created when the vendor
    does not exist.

    Creates a BakedGood with a vendor_id that is not present in
    the database and verifies that the repository raises a
    ValueError.

    Args:
        db: The SQLAlchemy database session used for the test.

    Returns:
        None.
    """

    repository = BakedGoodRepository(db)

    baked_good = BakedGood(
        active=True,
        name="Chocolate Cake",
        description="A chocolate cake",
        purchasing_cost=5.00,
        retail_price=10.00,
        vendor_id=9999,
    )

    with pytest.raises(ValueError, match="Vendor not found"):
        repository.create_baked_good(baked_good)
