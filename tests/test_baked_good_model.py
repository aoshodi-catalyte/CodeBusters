import pytest
from pydantic import ValidationError

from baked_good.baked_good_model import BakedGood

def test_valid_baked_good():
    """
    Tests that a baked good with valid data can be created successfully.

    Creates a BakedGood object using valid values and verifies that
    each field contains the expected value.

    Args:
        None

    Returns:
        None
    """
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
    """
    Tests that a baked good cannot be created with an empty name.

    Attempts to create a BakedGood object with an empty name and
    verifies that Pydantic raises a ValidationError.

    Args:
        None

    Returns:
        None
    """

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
    """
        Tests that a baked good cannot be created with an empty description.

        Attempts to create a BakedGood object with an empty description and
        verifies that Pydantic raises a ValidationError.

        Args:
            None

        Returns:
            None
        """
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
    """
    Tests that the purchasing cost cannot be negative.

    Attempts to create a BakedGood object with a negative purchasing cost
    and verifies that Pydantic raises a ValidationError.

    Args:
        None

    Returns:
        None
    """

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
    """
    Tests that the retail price cannot be negative.

    Attempts to create a BakedGood object with a negative retail price
    and verifies that Pydantic raises a ValidationError.

    Args:
        None

    Returns:
        None
    """
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
    """
    Tests that the retail price must be greater than the purchasing cost.

    Attempts to create a BakedGood object where the retail price is equal
    to the purchasing cost and verifies that Pydantic raises a
    ValidationError.

    Args:
        None

    Returns:
        None
    """

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
    """
    Tests that the retail price cannot be less than the purchasing cost.

    Attempts to create a BakedGood object where the retail price is less
    than the purchasing cost and verifies that Pydantic raises a
    ValidationError.

    Args:
        None

    Returns:
        None
    """
    with pytest.raises(ValidationError):
        BakedGood(
            id=1,
            active=True,
            name="Chocolate Cake",
            description="A chocolate cake",
            purchasing_cost=10.0,
            retail_price=5.0,
        )