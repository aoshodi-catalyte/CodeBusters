import pytest
from pydantic import ValidationError

from baked_good.baked_good_model import BakedGood, BakedGoodUpdate


def test_valid_baked_good():
    """
    Tests that a baked good with valid data can be created successfully.
    """
    baked_good = BakedGood(
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
            active=True,
            name="",
            description="A chocolate cake",
            purchasing_cost=10.0,
            retail_price=15.0,
            vendor_id=1
        )


def test_name_cannot_be_whitespace_only():
    """
    Tests that a baked good name consisting only of whitespace is rejected.
    """
    with pytest.raises(ValidationError):
        BakedGood(
            active=True,
            name="   ",
            description="A chocolate cake",
            purchasing_cost=10.0,
            retail_price=15.0,
            vendor_id=1
        )


def test_name_cannot_have_leading_or_trailing_whitespace():
    """
    Tests that a non-empty name with leading/trailing whitespace is
    rejected (as opposed to being silently stripped).
    """
    with pytest.raises(ValidationError):
        BakedGood(
            active=True,
            name=" Chocolate Cake",
            description="A chocolate cake",
            purchasing_cost=10.0,
            retail_price=15.0,
            vendor_id=1
        )

    with pytest.raises(ValidationError):
        BakedGood(
            active=True,
            name="Chocolate Cake ",
            description="A chocolate cake",
            purchasing_cost=10.0,
            retail_price=15.0,
            vendor_id=1
        )


def test_description_cannot_be_empty():
    with pytest.raises(ValidationError):
        BakedGood(
            active=True,
            name="Chocolate Cake",
            description="",
            purchasing_cost=10.0,
            retail_price=15.0,
            vendor_id=1
        )


def test_purchasing_cost_cannot_be_negative():
    with pytest.raises(ValidationError):
        BakedGood(
            active=True,
            name="Chocolate Cake",
            description="A chocolate cake",
            purchasing_cost=-10.0,
            retail_price=15.0,
            vendor_id=1
        )


def test_purchasing_cost_must_be_greater_than_zero():
    with pytest.raises(ValidationError):
        BakedGood(
            active=True,
            name="Chocolate Cake",
            description="A chocolate cake",
            purchasing_cost=0,
            retail_price=15.0,
            vendor_id=1
        )


def test_retail_price_cannot_be_negative():
    with pytest.raises(ValidationError):
        BakedGood(
            active=True,
            name="Chocolate Cake",
            description="A chocolate cake",
            purchasing_cost=10.0,
            retail_price=-15.0,
            vendor_id=1
        )


def test_retail_price_must_be_greater_than_purchasing_cost():
    with pytest.raises(ValidationError):
        BakedGood(
            active=True,
            name="Chocolate Cake",
            description="A chocolate cake",
            purchasing_cost=10.0,
            retail_price=10.0,
            vendor_id=1
        )


def test_retail_price_must_be_greater_than_zero():
    with pytest.raises(ValidationError):
        BakedGood(
            active=True,
            name="Chocolate Cake",
            description="A chocolate cake",
            purchasing_cost=10.0,
            retail_price=0,
            vendor_id=1
        )


def test_retail_price_cannot_be_less_than_purchasing_cost():
    with pytest.raises(ValidationError):
        BakedGood(
            active=True,
            name="Chocolate Cake",
            description="A chocolate cake",
            purchasing_cost=10.0,
            retail_price=5.0,
            vendor_id=1
        )


# --- BakedGoodUpdate ---
# BakedGoodUpdate currently adds no fields or validators beyond
# BakedGoodBase, so it should enforce the exact same rules as BakedGood.


def test_valid_baked_good_update():
    """
    Tests that a BakedGoodUpdate with valid data can be created successfully.
    """
    baked_good = BakedGoodUpdate(
        active=False,
        name="Sourdough Loaf",
        description="A tangy sourdough loaf",
        purchasing_cost=3.0,
        retail_price=7.0,
        vendor_id=2
    )

    assert baked_good.active is False
    assert baked_good.name == "Sourdough Loaf"
    assert baked_good.description == "A tangy sourdough loaf"
    assert baked_good.purchasing_cost == 3.0
    assert baked_good.retail_price == 7.0
    assert baked_good.vendor_id == 2


def test_baked_good_update_name_cannot_be_empty():
    with pytest.raises(ValidationError):
        BakedGoodUpdate(
            active=True,
            name="",
            description="A chocolate cake",
            purchasing_cost=10.0,
            retail_price=15.0,
            vendor_id=1
        )


def test_baked_good_update_name_cannot_have_leading_or_trailing_whitespace():
    with pytest.raises(ValidationError):
        BakedGoodUpdate(
            active=True,
            name=" Chocolate Cake",
            description="A chocolate cake",
            purchasing_cost=10.0,
            retail_price=15.0,
            vendor_id=1
        )


def test_baked_good_update_description_cannot_be_empty():
    with pytest.raises(ValidationError):
        BakedGoodUpdate(
            active=True,
            name="Chocolate Cake",
            description="",
            purchasing_cost=10.0,
            retail_price=15.0,
            vendor_id=1
        )


def test_baked_good_update_purchasing_cost_must_be_greater_than_zero():
    with pytest.raises(ValidationError):
        BakedGoodUpdate(
            active=True,
            name="Chocolate Cake",
            description="A chocolate cake",
            purchasing_cost=0,
            retail_price=15.0,
            vendor_id=1
        )


def test_baked_good_update_retail_price_must_be_greater_than_purchasing_cost():
    with pytest.raises(ValidationError):
        BakedGoodUpdate(
            active=True,
            name="Chocolate Cake",
            description="A chocolate cake",
            purchasing_cost=10.0,
            retail_price=10.0,
            vendor_id=1
        )


def test_baked_good_update_requires_all_fields():
    """
    Tests that BakedGoodUpdate requires every field (full-replace PUT
    semantics), since it does not define any defaults.
    """
    with pytest.raises(ValidationError):
        BakedGoodUpdate(
            name="Chocolate Cake",
            description="A chocolate cake",
            purchasing_cost=10.0,
            retail_price=15.0,
            vendor_id=1
        )
