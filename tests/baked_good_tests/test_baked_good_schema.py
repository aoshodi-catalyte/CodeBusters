import models

from sqlalchemy import Numeric, inspect

from baked_good.baked_good_schema import BakedGoodSchema


def test_baked_good_table_name():
    """
    Tests that the BakedGoodSchema uses the correct database table name.
    """

    assert BakedGoodSchema.__tablename__ == "baked_good"


def test_baked_good_columns():
    """
    Tests that the BakedGoodSchema contains the expected columns and data types.
    """

    columns = inspect(BakedGoodSchema).columns

    assert columns["id"].primary_key is True
    assert columns["active"].type.python_type is bool
    assert columns["name"].type.python_type is str
    assert columns["description"].type.python_type is str

    assert isinstance(columns["purchasing_cost"].type, Numeric)
    assert isinstance(columns["retail_price"].type, Numeric)

    assert columns["purchasing_cost"].type.scale == 2
    assert columns["retail_price"].type.scale == 2


def test_description_is_required():
    """
    Tests that the baked good description is required.
    """

    columns = inspect(BakedGoodSchema).columns

    assert columns["description"].nullable is False


def test_name_is_required():
    """
    Tests that the baked good name is required.
    """

    columns = inspect(BakedGoodSchema).columns

    assert columns["name"].nullable is False


def test_id_is_unique_primary_key():
    """
    Tests that the baked good ID is configured as the primary key.
    """

    columns = inspect(BakedGoodSchema).columns

    assert columns["id"].primary_key is True


def test_vendor_relationship_exists():
    relationships = inspect(BakedGoodSchema).relationships

    assert "vendor" in relationships

    relationship = relationships["vendor"]

    assert relationship.mapper.class_.__name__ == "Vendor"
    assert relationship.back_populates == "baked_good"


def test_vendor_id_foreign_key():
    columns = inspect(BakedGoodSchema).columns

    foreign_keys = columns["vendor_id"].foreign_keys

    assert any(fk.target_fullname == "vendor.id" for fk in foreign_keys)


def test_vendor_id_is_required():
    """
    Tests that the baked good vendor ID is required.
    """

    columns = inspect(BakedGoodSchema).columns

    assert columns["vendor_id"].nullable is False
