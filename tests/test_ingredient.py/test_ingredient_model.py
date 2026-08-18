import pytest
from pydantic import ValidationError
from ingredient.ingredient_model import Allergen, Ingredient
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
        purchasing_cost=4.50,
        unit_amount=1.00,
        unit_of_measure=UnitOfMeasure.liters,
        allergens=["milk"],
        vendor_id=1,
    )

    assert ingredient.active is True
    assert ingredient.name == "Whole Milk"
    assert ingredient.purchasing_cost == 4.50
    assert ingredient.unit_amount == 1.00
    assert ingredient.unit_of_measure == UnitOfMeasure.liters
    assert ingredient.allergens == ["Milk"]
    assert ingredient.vendor_id == 1


def test_ingredient_active_defaults_to_true():
    ingredient = Ingredient(
        active=True,
        name="Whole Milk",
        purchasing_cost=4.50,
        unit_amount=1.00,
        unit_of_measure=UnitOfMeasure.liters,
        vendor_id=1,
    )

    assert ingredient.active is True


def test_ingredient_allergens_default_to_empty_list():
    ingredient = Ingredient(
        name="Whole Milk",
        purchasing_cost=4.50,
        unit_amount=1.00,
        unit_of_measure=UnitOfMeasure.liters,
        vendor_id=1,
    )

    assert ingredient.allergens == []


def test_purchasing_cost_cannot_be_negative():
    with pytest.raises(ValidationError):
        Ingredient(
            name="Whole Milk",
            purchasing_cost=-4.50,
            unit_amount=1.00,
            unit_of_measure=UnitOfMeasure.liters,
            vendor_id=1,
        )


def test_unit_amount_must_be_greater_than_zero():
    with pytest.raises(ValidationError):
        Ingredient(
            name="Whole Milk",
            purchasing_cost=4.50,
            unit_amount=-1.00,
            unit_of_measure=UnitOfMeasure.liters,
            vendor_id=1,
        )


def test_unit_of_measure():
    ingredient = Ingredient(
        name="Whole Milk",
        purchasing_cost=4.50,
        unit_amount=1.00,
        unit_of_measure=UnitOfMeasure.liters,
        vendor_id=1,
    )

    assert ingredient.unit_of_measure == UnitOfMeasure.liters

def test_create_ingredient_with_empty_allergens():
    ingredient = Ingredient(
        name="Flour",
        purchasing_cost=4.50,
        unit_amount=1.00,
        unit_of_measure=UnitOfMeasure.kilograms,
        allergens=[],
        vendor_id=1,
    )

    assert ingredient.allergens == []
def test_invalid_allergen_raises_validation_error():
    """
    Test that an invalid allergen value raises a Pydantic
    validation error.
    """
    with pytest.raises(ValidationError):
        Ingredient(
            name="Mystery Item",
            purchasing_cost=4.50,
            unit_amount=1.00,
            unit_of_measure=UnitOfMeasure.liters,
            allergens=["Kryptonite"],
            vendor_id=1,
        )
def test_invalid_unit_of_measure_raises_validation_error():
    """
    Test that an invalid unit of measure raises a Pydantic
    validation error.
    """
    with pytest.raises(ValidationError):
        Ingredient(
            name="Mystery Item",
            purchasing_cost=4.50,
            unit_amount=1.00,
            unit_of_measure="parsecs",
            allergens=[],
            vendor_id=1,
        )