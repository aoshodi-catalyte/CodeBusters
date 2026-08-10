import pytest
from vendor.vendor_schema import Vendor, VendorSchema

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