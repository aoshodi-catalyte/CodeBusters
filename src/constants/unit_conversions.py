"""
Unit conversion table and helper function for recipe ingredient measurement
normalization.

This module defines a mapping of supported unit‑to‑unit conversions used when
calculating ingredient costs for drink recipes. Each conversion represents the
multiplicative factor required to convert a quantity from one unit of measure
into another (e.g., ounces → grams, gallons → milliliters).

The conversion system is used by the DrinkRecipeRepository to translate
recipe‑specific ingredient usage units into the ingredient's purchase unit,
ensuring accurate cost computation regardless of how the recipe measures its
ingredients.

UNIT_CONVERSIONS:
    A dictionary where each key is a (from_unit, to_unit) tuple and each value
    is the numeric conversion factor. For example:
        ("oz", "g"): 28.3495
        ("gal", "ml"): 3785.41
        ("lb", "oz"): 16

convert(amount, from_unit, to_unit):
    Converts a numeric quantity from one unit of measure into another using the
    UNIT_CONVERSIONS table. Raises a ValueError if the conversion is not
    supported. Returns the converted amount as a float.
"""


UNIT_CATEGORY = {
    "g": "weight",
    "kg": "weight",
    "oz": "weight",
    "lb": "weight",
    "scoop": "weight",

    "ml": "volume",
    "l": "volume",
    "fl_oz": "volume",
    "gal": "volume",
    "pump": "volume",
    "shot": "volume",
    "dash": "volume",
}

BASE_UNIT = {
    "weight": "g",
    "volume": "ml",
}

# Conversion factors into base units (g or ml)
TO_BASE = {
    # Weight → grams
    "g": 1,
    "kg": 1000,
    "oz": 28.3495,
    "lb": 453.592,
    "scoop": 5,

    # Volume → milliliters
    "ml": 1,
    "l": 1000,
    "fl_oz": 29.5735,
    "gal": 3785.41,
    "pump": 10,
    "shot": 30,       # espresso shot
    "dash": 0.9,      # bitters dash
}


def convert(amount: float, from_unit: str, to_unit: str) -> float:
    """
    Normalized unit conversion for drink measurements.
    Converts weight units via grams and volume units via milliliters.
    """

    if from_unit == to_unit:
        return amount

    if from_unit not in UNIT_CATEGORY:
        raise ValueError(f"Unsupported unit: {from_unit}")

    if to_unit not in UNIT_CATEGORY:
        raise ValueError(f"Unsupported unit: {to_unit}")

    from_cat = UNIT_CATEGORY[from_unit]
    to_cat = UNIT_CATEGORY[to_unit]

    # Prevent weight ↔ volume conversions
    if from_cat != to_cat:
        raise ValueError(
            f"Cannot convert between weight ({from_unit}) and volume ({to_unit})"
        )

    # Step 1: convert to base (g or ml)
    base_amount = amount * TO_BASE[from_unit]

    # Step 2: convert base → target
    return base_amount / TO_BASE[to_unit]
