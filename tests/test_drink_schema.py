from sqlalchemy import Integer, String, Float, Boolean
from drink_recipe.drink_recipe_schema import DrinkRecipeSchema # type: ignore


def test_table_name():
    assert DrinkRecipeSchema.__tablename__ == "drink_recipe"


def test_columns_exist():
    columns = DrinkRecipeSchema.__table__.columns

    assert "id" in columns
    assert "name" in columns
    assert "description" in columns
    assert "active" in columns
    assert "type_id" in columns
    assert "production_cost" in columns


def test_column_types():
    columns = DrinkRecipeSchema.__table__.columns

    assert isinstance(columns["id"].type, Integer)
    assert isinstance(columns["name"].type, String)
    assert isinstance(columns["description"].type, String)
    assert isinstance(columns["active"].type, Boolean)
    assert isinstance(columns["type_id"].type, Integer)
    assert isinstance(columns["production_cost"].type, Float)


def test_primary_key():
    pk = DrinkRecipeSchema.__table__.primary_key.columns
    assert "id" in pk


def test_nullable_constraints():
    columns = DrinkRecipeSchema.__table__.columns

    assert columns["name"].nullable is False
    assert columns["description"].nullable is False
    assert columns["type_id"].nullable is False


def test_relationship_exists():
    # SQLAlchemy stores relationships in __mapper__.relationships
    relationships = DrinkRecipeSchema.__mapper__.relationships

    assert "recipe_ingredients" in relationships

    rel = relationships["recipe_ingredients"]

    # Relationship points to IngredientSchema
    assert rel.mapper.class_.__name__ == "DrinkRecipeIngredientSchema"

    # Relationship is configured with back_populates
    assert rel.back_populates == "drink_recipe"
