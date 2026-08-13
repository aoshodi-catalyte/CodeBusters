import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base
from vendor.vendor_model import VendorBase
from vendor.vendor_schema import Vendor
from repositories.vendor_repository import VendorRepository
from ingredient.ingredient_schema import IngredientSchema, AllergenSchema
from baked_good.baked_good_schema import BakedGoodSchema


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


def test_create_new_vendor(db_session):
    repo = VendorRepository(db_session)
    vendor_data = VendorBase(
        active=True,
        name="Bob's Burgers",
        contact_name="Bob Belcher",
        contact_role="CEO",
        email="bestburgers@burger.com",
        phone="1234567896"
    )

    created_vendor = repo.create_new_vendor(vendor_data)

    assert created_vendor.id is not None
    assert created_vendor.name == "Bob's Burgers"
    assert created_vendor.email == "bestburgers@burger.com"


def test_get_all_vendors_returns_created_vendors(db_session):
    repo = VendorRepository(db_session)
    repo.create_new_vendor(VendorBase(
        active=True,
        name="Bob's Burgers",
        contact_name="Bob Belcher",
        contact_role="CEO",
        email="bestburgers@burger.com",
        phone="1234567896"
    ))
    repo.create_new_vendor(VendorBase(
        active=True,
        name="Linda's Bakery",
        contact_name="Linda Belcher",
        contact_role="Owner",
        email="linda@bakery.com",
        phone="9876543210"
    ))

    all_vendors = repo.get_all_vendors()

    assert len(all_vendors) == 2


def test_get_vendor_by_id_returns_correct_vendor(db_session):
    repo = VendorRepository(db_session)
    created_vendor = repo.create_new_vendor(VendorBase(
        active=True,
        name="Bob's Burgers",
        contact_name="Bob Belcher",
        contact_role="CEO",
        email="bestburgers@burger.com",
        phone="1234567896"
    ))

    fetched_vendor = repo.get_vendor_by_id(created_vendor.id)

    assert fetched_vendor is not None
    assert fetched_vendor.name == "Bob's Burgers"


def test_get_vendor_by_id_returns_none_when_not_found(db_session):
    repo = VendorRepository(db_session)

    result = repo.get_vendor_by_id(999)

    assert result is None


def test_vendor_ingredients_relationship(db_session):
    repo = VendorRepository(db_session)
    vendor = repo.create_new_vendor(VendorBase(
        active=True,
        name="Bob's Burgers Supply Co",
        contact_name="Bob Belcher",
        contact_role="CEO",
        email="supplyco@burger.com",
        phone="1234567896"
    ))

    ingredient = IngredientSchema(
        active=True,
        name="Ground Beef",
        purchasing_cost=12.50,
        unit_amount=5,
        unit_of_measure="lb",
        vendor_id=vendor.id
    )
    db_session.add(ingredient)
    db_session.commit()
    db_session.refresh(vendor)

    assert len(vendor.ingredients) == 1
    assert vendor.ingredients[0].name == "Ground Beef"
    assert ingredient.vendor.name == "Bob's Burgers Supply Co"