from decimal import Decimal

import pytest
from pydantic import ValidationError

from ingredient_model import Allergen, Ingredient
from constants.INGREDIENT_TYPES import UnitOfMeasure


def test_allergen():
    allergen = Allergen(name="milk")

    assert allergen.name == "milk"


def test_allergen_name_cannot_be_empty():
    with pytest.raises(ValidationError):
        Allergen(name="")


def test_ingredient():
    ingredient = Ingredient(
        active=True,
        name="Whole Milk",
        purchasing_cost=Decimal("4.50"),
        unit_amount=Decimal("1.00"),
        unit_of_measure=UnitOfMeasure.liters,
        allergens=["milk"],
    )

    assert ingredient.active is True
    assert ingredient.name == "Whole Milk"
    assert ingredient.purchasing_cost == Decimal("4.50")
    assert ingredient.unit_amount == Decimal("1.00")
    assert ingredient.unit_of_measure == UnitOfMeasure.liters
    assert ingredient.allergens == ["milk"]


def test_ingredient_active_defaults_to_true():
    ingredient = Ingredient(
        name="Whole Milk",
        purchasing_cost=Decimal("4.50"),
        unit_amount=Decimal("1.00"),
        unit_of_measure=UnitOfMeasure.liters,
    )

    assert ingredient.active is True


def test_ingredient_allergens_default_to_empty_list():
    ingredient = Ingredient(
        name="Whole Milk",
        purchasing_cost=Decimal("4.50"),
        unit_amount=Decimal("1.00"),
        unit_of_measure=UnitOfMeasure.liters,
    )

    assert ingredient.allergens == []


def test_purchasing_cost_cannot_be_negative():
    with pytest.raises(ValidationError):
        Ingredient(
            name="Whole Milk",
            purchasing_cost=Decimal("-1.00"),
            unit_amount=Decimal("1.00"),
            unit_of_measure=UnitOfMeasure.liters,
        )


def test_unit_amount_must_be_greater_than_zero():
    with pytest.raises(ValidationError):
        Ingredient(
            name="Whole Milk",
            purchasing_cost=Decimal("4.50"),
            unit_amount=Decimal("0"),
            unit_of_measure=UnitOfMeasure.liters,
        )


def test_unit_of_measure():
    ingredient = Ingredient(
        name="Coffee",
        purchasing_cost=Decimal("15.00"),
        unit_amount=Decimal("1.00"),
        unit_of_measure=UnitOfMeasure.kilograms,
    )

    assert ingredient.unit_of_measure == UnitOfMeasure.kilograms