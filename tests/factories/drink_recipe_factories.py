"""
Factories for drink recipe tests, including drink types, ingredient creation,
router payload builders, and ORM model builders. These utilities ensure
consistent, repeatable test setup across router and repository test suites.
"""

import pytest

from drink_recipe.drink_recipe_model import DrinkRecipe, RecipeIngredient
from drink_recipe.drink_type_schema import DrinkTypeSchema
from ingredient.ingredient_schema import IngredientSchema


@pytest.fixture
def drink_types(db):
    """Provides all drink types used in tests."""
    types = [
        DrinkTypeSchema(name="coffee"),
        DrinkTypeSchema(name="tea"),
        DrinkTypeSchema(name="soda"),
        DrinkTypeSchema(name="other"),
    ]
    db.add_all(types)
    db.commit()
    return {t.name.lower(): t for t in types}


@pytest.fixture
def ingredient_factory(db):
    """Creates and persists ingredients quickly."""
    def create(name="Milk", cost=8.00, amount=1.00, uom="gal", vendor_id=1):
        ing = IngredientSchema(
            name=name,
            purchasing_cost=cost,
            unit_amount=amount,
            unit_of_measure=uom,
            vendor_id=vendor_id,
        )
        db.add(ing)
        db.commit()
        return ing
    return create


@pytest.fixture
def recipe_payload_factory():
    """Builds drink recipe payload dictionaries for router tests."""
    def create(name, description, ingredients, drink_type="coffee", markup=81, active=True): # pylint: disable=R0913, R0917
        return {
            "name": name,
            "description": description,
            "ingredients": [
                {
                    "id": ing.id,
                    "quantity_used": qty,
                    "unit_of_measure_used": uom,
                }
                for ing, qty, uom in ingredients
            ],
            "active": active,
            "type": drink_type,
            "markup_percentage": markup,
        }
    return create


@pytest.fixture
def recipe_model_factory():
    """Builds DrinkRecipe ORM models for repository tests."""
    def create(name, description, ingredients, drink_type="coffee", markup=81, active=True): # pylint: disable=R0913, R0917
        return DrinkRecipe(
            name=name,
            description=description,
            ingredients=[
                RecipeIngredient(id=ing.id, quantity_used=qty, unit_of_measure_used=uom)
                for ing, qty, uom in ingredients
            ],
            active=active,
            type=drink_type,
            markup_percentage=markup,
        )
    return create
