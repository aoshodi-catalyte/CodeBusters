# src/utils/validators.py

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
