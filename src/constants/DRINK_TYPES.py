from enum import Enum

class DrinkType(str, Enum):
    COFFEE = "coffee"
    TEA = "tea"
    OTHER = "other"