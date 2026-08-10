from enum import Enum

class UnitOfMeasure(str, Enum):
    grams = "g"
    kilograms = "kg"
    ounces = "oz"
    pounds = "lb"
    fluid_ounces = "fl_oz"
    milliliters = "ml"
    liters = "l"
    gallons = "gal"
    pumps = "pump"
    scoops = "scoop"
    shots = "shot"
    dashes = "dash"