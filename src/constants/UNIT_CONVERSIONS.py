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


UNIT_CONVERSIONS = {
    ("lb", "g"): 453.592,
    ("g", "lb"): 1 / 453.592,

    ("oz", "g"): 28.3495,
    ("g", "oz"): 1 / 28.3495,

    ("tsp", "g"): 4.2,
    ("tbsp", "g"): 12.6,

    ("cup", "ml"): 240,
    ("ml", "cup"): 1 / 240,

    # --- Gallon conversions ---
    ("gal", "ml"): 3785.41,
    ("ml", "gal"): 1 / 3785.41,

    ("gal", "l"): 3.78541,
    ("l", "gal"): 1 / 3.78541,

    ("gal", "oz"): 128,
    ("oz", "gal"): 1 / 128,

    ("gal", "cup"): 16,
    ("cup", "gal"): 1 / 16,

    # --- Pound ↔ Ounce conversions (required for espresso beans) ---
    ("lb", "oz"): 16,
    ("oz", "lb"): 1 / 16,
}


def convert(amount: float, from_unit: str, to_unit: str) -> float:
    """
    Args:
        amount (float):
            The numeric quantity to convert.

        from_unit (str):
            The unit of measurement the amount is currently expressed in
            (e.g., "oz", "g", "tsp").

        to_unit (str):
            The unit of measurement to convert the amount into.

    Returns:
        float: The converted quantity expressed in the target unit.

    Raises:
        ValueError: If no conversion exists between the specified units.
    """
    
    if from_unit == to_unit:
        return amount
    key = (from_unit, to_unit)
    if key not in UNIT_CONVERSIONS:
        raise ValueError(f"No conversion from {from_unit} to {to_unit}")
    return amount * float(str(UNIT_CONVERSIONS[key]))
