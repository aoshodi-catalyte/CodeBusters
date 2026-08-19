"""
Utility helpers for enum normalization and case-insensitive lookup.
"""


def enum_missing_handler(cls, value):
    """
    Shared logic for case-insensitive enum value lookup.

    Args:
        cls (Enum): The enum class calling this helper.
        value (Any): The raw value passed to `_missing_`.

    Returns:
        Enum | None: The matched enum member or None.
    """
    if isinstance(value, str):
        value = value.lower()
        if value in cls._value2member_map_:
            return cls._value2member_map_[value]
    return None
