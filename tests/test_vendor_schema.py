import pytest
from pydantic import ValidationError

from vendor.vendor_schema import VendorSchema


def test_vendor_schema_valid_data():
    vendor_example = VendorSchema(
        id=1,
        active=True,
        name="Bob's Burgers",
        contact_name="Bob Belcher",
        contact_role="CEO",
        email="bestBurgers@burger.com",
        phone="123-456-7896"
    )

    assert vendor_example.email == "bestBurgers@burger.com"
    assert vendor_example.phone == "1234567896"


def test_vendor_schema_invalid_email_raises():
    with pytest.raises(ValidationError):
        VendorSchema(
            id=1,
            active=True,
            name="Bob's Burgers",
            contact_name="Bob Belcher",
            contact_role="CEO",
            email="not-a-valid-email",
            phone="1234567896"
        )


def test_vendor_schema_invalid_phone_raises():
    with pytest.raises(ValidationError):
        VendorSchema(
            id=1,
            active=True,
            name="Bob's Burgers",
            contact_name="Bob Belcher",
            contact_role="CEO",
            email="bestBurgers@burger.com",
            phone="123" 
        )