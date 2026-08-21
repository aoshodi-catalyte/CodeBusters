<<<<<<< HEAD
# src/utils/validators.py
=======
"""
Utility functions for numeric validation and rounding.

Provides helpers such as `round_float`, which performs precise rounding of
float values using Decimal to avoid binary floating‑point inaccuracies.
"""
>>>>>>> fc4504c683cea032e2b8da45d105264ab33944c0

from decimal import Decimal, ROUND_HALF_UP

def round_float(value: float, places: int = 2) -> float:
    """
    Safely round a float to a fixed number of decimal places using Decimal
    for precision, then return a float.

    Args:
        value (float): The input float.
        places (int): Number of decimal places to round to.

    Returns:
        float: Rounded float.
    """
    q = Decimal("1." + "0" * places)
    return float(Decimal(str(value)).quantize(q, rounding=ROUND_HALF_UP))
