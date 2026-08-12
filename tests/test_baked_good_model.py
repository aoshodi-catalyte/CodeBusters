import pytest
from pydantic import ValidationError

from baked_good.baked_good_model import BakedGood

def test_valid_baked_good():
    baked_good = BakedGood(
        id=1,
        active=True,
        name="Chocolate Cake",
        description="A chocolate cake",
        purchasing_cost=10.0,
        retail_price=15.0,
        vendor_id=1
    )

    assert baked_good.active is True
    assert baked_good.name == "Chocolate Cake"
    assert baked_good.description == "A chocolate cake"
    assert baked_good.purchasing_cost == 10.0
    assert baked_good.retail_price == 15.0
    assert baked_good.vendor_id == 1

    def test_name_cannot_be_empty():
        with pytest.raises(ValidationError):
            BakedGood(
                id=1,
                active=True,
                name="",
                description="A chocolate cake",
                purchasing_cost=10.0,
                retail_price=15.0,
        )

    def test_description_cannot_be_empty():
        with pytest.raises(ValidationError):
            BakedGood(
                id=1,
                active=True,
                name="Chocolate Cake",
                description="",
                purchasing_cost=10.0,
                retail_price=15.0,
        )

    def test_purchasing_cost_cannot_be_negative():
        with pytest.raises(ValidationError):
            BakedGood(
                id=1,
                active=True,
                name="Chocolate Cake",
                description="A chocolate cake",
                purchasing_cost=-10.0,
                retail_price=15.0,
        )

def test_retail_price_cannot_be_negative():
    with pytest.raises(ValidationError):
        BakedGood(
            id=1,
            active=True,
            name="Chocolate Cake",
            description="A chocolate cake",
            purchasing_cost=10.0,
            retail_price=-15.0,
        )   

def test_retail_price_must_be_greater_than_purchasing_cost():
    with pytest.raises(ValidationError):
        BakedGood(
            id=1,
            active=True,
            name="Chocolate Cake",
            description="A chocolate cake",
            purchasing_cost=10.0,
            retail_price=10.0,
        )

def test_retail_price_cannot_be_less_than_purchasing_cost():
    with pytest.raises(ValidationError):
        BakedGood(
            id=1,
            active=True,
            name="Chocolate Cake",
            description="A chocolate cake",
            purchasing_cost=10.0,
            retail_price=5.0,
        )