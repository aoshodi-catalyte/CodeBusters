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
        lowered = value.lower()

        # __members__ is the public, pylint-safe mapping
        for member_name, member in cls.__members__.items():
            if member.value.lower() == lowered:
                return member

    return None
