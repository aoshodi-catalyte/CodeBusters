# from sqlalchemy import inspect

# from baked_good.baked_good_schema import BakedGoodSchema

# def test_baked_good_table_name():
#     assert BakedGoodSchema.__tablename__ == "baked_goods"

# def test_baked_good_columns():
#     columns = inspect(BakedGoodSchema).columns

#     assert columns["id"].primary_key is True
#     assert columns["active"].type.python_type is bool
#     assert columns["name"].type.python_type is str
#     assert columns["description"].type.python_type is str
#     assert columns["purchasing_cost"].type.python_type is float
#     assert columns["retail_price"].type.python_type is float

# def test_description_is_required():
#     columns = inspect(BakedGoodSchema).columns

#     assert columns["description"].nullable is False

# def test_name_is_required():
#     columns = inspect(BakedGoodSchema).columns

#     assert columns["name"].nullable is False

# def test_id_is_unique_primary_key():
#     columns = inspect(BakedGoodSchema).columns

#     assert columns["id"].primary_key is True
#     assert columns["id"].unique is False