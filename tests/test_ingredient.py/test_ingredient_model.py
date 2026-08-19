"""Tests for ingredient Pydantic models."""

import pytest
from pydantic import ValidationError

from constants.ingredient_types import UnitOfMeasure
from ingredient.ingredient_model import Allergen, Ingredient


def test_allergen():
    """Test that an allergen can be created successfully."""
    allergen = Allergen(name="milk")

    assert allergen.name == "milk"


def test_allergen_name_cannot_be_empty():
    """Test that an allergen name cannot be empty."""
    with pytest.raises(ValidationError):
        Allergen(name="")


def test_ingredient():
    """Test that an ingredient can be created successfully."""
    ingredient = Ingredient(
        active=True,
        name="Whole Milk",
        purchasing_cost=4.50,
        unit_amount=1.00,
        unit_of_measure=UnitOfMeasure.LITERS,
        allergens=["milk"],
        vendor_id=1,
    )

    assert ingredient.active is True
    assert ingredient.name == "Whole Milk"
    assert ingredient.purchasing_cost == 4.50
    assert ingredient.unit_amount == 1.00
    assert ingredient.unit_of_measure == UnitOfMeasure.LITERS
    assert ingredient.allergens == ["Milk"]
    assert ingredient.vendor_id == 1


def test_ingredient_active_defaults_to_true():
    """Test that active defaults to True."""
    ingredient = Ingredient(
        name="Whole Milk",
        purchasing_cost=4.50,
        unit_amount=1.00,
        unit_of_measure=UnitOfMeasure.LITERS,
        vendor_id=1,
    )

    assert ingredient.active is True


def test_ingredient_allergens_default_to_empty_list():
    """Test that allergens default to an empty list."""
    ingredient = Ingredient(
        name="Whole Milk",
        purchasing_cost=4.50,
        unit_amount=1.00,
        unit_of_measure=UnitOfMeasure.LITERS,
        vendor_id=1,
    )

    assert ingredient.allergens == []


def test_purchasing_cost_cannot_be_negative():
    """Test that purchasing cost cannot be negative."""
    with pytest.raises(ValidationError):
        Ingredient(
            name="Whole Milk",
            purchasing_cost=-4.50,
            unit_amount=1.00,
            unit_of_measure=UnitOfMeasure.LITERS,
            vendor_id=1,
        )


def test_unit_amount_must_be_greater_than_zero():
    """Test that unit amount must be greater than zero."""
    with pytest.raises(ValidationError):
        Ingredient(
            name="Whole Milk",
            purchasing_cost=4.50,
            unit_amount=-1.00,
            unit_of_measure=UnitOfMeasure.LITERS,
            vendor_id=1,
        )


def test_unit_of_measure():
    """Test that a valid unit of measure is accepted."""
    ingredient = Ingredient(
        name="Whole Milk",
        purchasing_cost=4.50,
        unit_amount=1.00,
        unit_of_measure=UnitOfMeasure.LITERS,
        vendor_id=1,
    )

    assert ingredient.unit_of_measure == UnitOfMeasure.LITERS


def test_create_ingredient_with_empty_allergens():
    """Test that an ingredient can have no allergens."""
    ingredient = Ingredient(
        name="Flour",
        purchasing_cost=4.50,
        unit_amount=1.00,
        unit_of_measure=UnitOfMeasure.KILOGRAMS,
        allergens=[],
        vendor_id=1,
    )

    assert ingredient.allergens == []


def test_invalid_allergen_raises_validation_error():
    """Test that an invalid allergen raises a validation error."""
    with pytest.raises(ValidationError):
        Ingredient(
            name="Mystery Item",
            purchasing_cost=4.50,
            unit_amount=1.00,
            unit_of_measure=UnitOfMeasure.LITERS,
            allergens=["Kryptonite"],
            vendor_id=1,
        )


def test_invalid_unit_of_measure_raises_validation_error():
    """Test that an invalid unit raises a validation error."""
    with pytest.raises(ValidationError):
        Ingredient(
            name="Mystery Item",
            purchasing_cost=4.50,
            unit_amount=1.00,
            unit_of_measure="parsecs",
            allergens=[],
            vendor_id=1,
        )