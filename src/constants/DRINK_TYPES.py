"""
Enumeration of supported drink categories.

    This enum defines the valid drink type values that can be assigned to
    a drink recipe. Each value corresponds to a category stored in the
    drink_type database table and is used for request validation,
    repository logic, and response serialization.
"""

from enum import Enum

class DrinkType(str, Enum):
    """
    Enumeration of supported drink categories.

    This enum defines the valid drink type values that can be assigned to a
    drink recipe. Each value corresponds to a category stored in the drink_type
    database table and is used for request validation, repository logic, and
    response serialization.

    Members:
        COFFEE:
            Represents coffee-based drinks.

        TEA:
            Represents tea-based drinks.

        SODA:
            Represents carbonated soft drinks such as cola, root beer, or
            flavored sparkling beverages.

        OTHER:
            Represents drinks that do not fall into the coffee, tea, or soda
            categories (e.g., smoothies, juices, specialty beverages).
    """
    
    COFFEE = "coffee"
    TEA = "tea"
    SODA = "soda"
    OTHER = "other"

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            value = value.lower()
            if value in cls._value2member_map_:
                return cls._value2member_map_[value]
        return None