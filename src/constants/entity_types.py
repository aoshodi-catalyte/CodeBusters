from enum import Enum

from utils.enum_handler import enum_missing_handler

class EntityType(str, Enum):
    """
    Enumeration of valid entity types within the system.
    """

    VENDOR = "vendor"
    INGREDIENT = "ingredient"
    BAKED_GOOD = "baked good"
    DRINK_RECIPE = "drink recipe"
    CUSTOMER = "customer"
    EMPLOYEE = "employee"
    PROMOTION = "promotion"
    PURCHASE = "purchase"

    @classmethod
    def _missing_(cls, value: object):
        return enum_missing_handler(cls, value)