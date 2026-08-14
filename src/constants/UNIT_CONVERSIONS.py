

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
    if from_unit == to_unit:
        return amount
    key = (from_unit, to_unit)
    if key not in UNIT_CONVERSIONS:
        raise ValueError(f"No conversion from {from_unit} to {to_unit}")
    return amount * float(str(UNIT_CONVERSIONS[key]))
