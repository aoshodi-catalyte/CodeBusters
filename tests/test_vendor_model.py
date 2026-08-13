import pytest
from vendor.vendor_schema import Vendor
from ingredient.ingredient_schema import IngredientSchema
from baked_good.baked_good_schema import BakedGoodSchema


def test_vendor_information():
    vendor_example = Vendor(
        active=True,
        name="Bob's Burgers",
        contact_name="Bob Belcher",
        contact_role="CEO",
        email="bestBurgers@burger.com",
        phone="1234567896"
    )

    assert vendor_example.active == True
    assert vendor_example.name == "Bob's Burgers"
    assert vendor_example.contact_name == "Bob Belcher"
    assert vendor_example.contact_role == "CEO"
    assert vendor_example.email == "bestBurgers@burger.com"
    assert vendor_example.phone == "1234567896"


def test_vendor_inactive_status():
    vendor_example = Vendor(
        active=False,
        name="Linda's Bakery",
        contact_name="Linda Belcher",
        contact_role="Owner",
        email="linda@bakery.com",
        phone="9876543210"
    )

    assert vendor_example.active == False
    assert vendor_example.name == "Linda's Bakery"


def test_vendor_different_contact_role():
    vendor_example = Vendor(
        active=True,
        name="Teddy's Repairs",
        contact_name="Teddy",
        contact_role="Manager",
        email="teddy@repairs.com",
        phone="5551234567"
    )

    assert vendor_example.contact_role == "Manager"
