import models

from sqlalchemy import inspect


from baked_good.baked_good_schema import BakedGoodSchema


def test_baked_good_table_name():
    """
    Tests that the BakedGoodSchema uses the correct database table name.

    Verifies that the SQLAlchemy model is mapped to the "baked_goods"
    database table.

    Args:
        None

    Returns:
        None
    """

    assert BakedGoodSchema.__tablename__ == "baked_goods"


def test_baked_good_columns():
    """
    Tests that the BakedGoodSchema contains the expected columns and data types.

    Inspects the SQLAlchemy model and verifies that the ID is the primary key
    and that each baked good field uses the expected Python data type.

    Args:
        None

    Returns:
        None
    """

    columns = inspect(BakedGoodSchema).columns

    assert columns["id"].primary_key is True
    assert columns["active"].type.python_type is bool
    assert columns["name"].type.python_type is str
    assert columns["description"].type.python_type is str
    assert columns["purchasing_cost"].type.python_type is float
    assert columns["retail_price"].type.python_type is float


def test_description_is_required():
    """
    Tests that the baked good description is required.

    Inspects the description column and verifies that it does not allow
    NULL values in the database.

    Args:
        None

    Returns:
        None
    """

    columns = inspect(BakedGoodSchema).columns

    assert columns["description"].nullable is False


def test_name_is_required():
    """
    Tests that the baked good name is required.

    Inspects the name column and verifies that it does not allow NULL
    values in the database.

    Args:
        None

    Returns:
        None
    """

    columns = inspect(BakedGoodSchema).columns

    assert columns["name"].nullable is False


def test_id_is_unique_primary_key():
    """
    Tests that the baked good ID is configured as the primary key.

    Inspects the ID column and verifies that it is configured as the
    primary key for the baked goods table.

    Args:
        None

    Returns:
        None
    """
    columns = inspect(BakedGoodSchema).columns

    assert columns["id"].primary_key is True


def test_vendor_relationship_exists():
    relationships = inspect(BakedGoodSchema).relationships

    assert "vendor" in relationships

    relationship = relationships["vendor"]

    assert relationship.mapper.class_.__name__ == "Vendor"
    assert relationship.back_populates == "baked_goods"


def test_vendor_id_foreign_key():
    columns = inspect(BakedGoodSchema).columns

    foreign_keys = columns["vendor_id"].foreign_keys

    assert any(fk.target_fullname == "vendor.id" for fk in foreign_keys)


def test_vendor_id_is_required():
    """
    Tests that the baked good vendor ID is required.

    Inspects the vendor_id column and verifies that it does not allow
    NULL values in the database.

    Args:
        None

    Returns:
        None
    """

    columns = inspect(BakedGoodSchema).columns

    assert columns["vendor_id"].nullable is False
