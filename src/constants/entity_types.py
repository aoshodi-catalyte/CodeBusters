"""
Defines the EntityType enumeration used throughout the system to
represent the different entity categories. These integer values map
directly to the seeded entity_type table in the audit database.
"""

from enum import IntEnum

from utils.enum_handler import enum_missing_handler

class EntityType(IntEnum):
    """
    Enumeration of valid entity types within the system.
    """

    VENDOR = 1
    INGREDIENT = 2
    BAKED_GOOD = 3
    DRINK_RECIPE = 4
    CUSTOMER = 5
    EMPLOYEE = 6
    PROMOTION = 7
    PURCHASE = 8


    def label(self) -> str:
        """
        Returns the human‑readable string label associated with this
        entity type. Used when seeding the entity_type table and when
        displaying audit records.
        """
        return {
            EntityType.VENDOR: "vendor",
            EntityType.INGREDIENT: "ingredient",
            EntityType.BAKED_GOOD: "baked good",
            EntityType.DRINK_RECIPE: "drink recipe",
            EntityType.CUSTOMER: "customer",
            EntityType.EMPLOYEE: "employee",
            EntityType.PROMOTION: "promotion",
            EntityType.PURCHASE: "purchase",
        }[self]


    @classmethod
    def _missing_(cls, value: object):
        """
        Handles invalid enum lookups by delegating to the shared
        enum_missing_handler utility.
        """
        return enum_missing_handler(cls, value)
