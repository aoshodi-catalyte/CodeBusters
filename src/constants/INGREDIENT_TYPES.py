"""Enums for ingredient units of measure and cafe allergens."""

from enum import Enum


class UnitOfMeasure(str, Enum):
    """Supported units of measure for ingredients."""

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

    @classmethod
    def from_string(cls, value: str) -> "UnitOfMeasure":
        """Convert a string or alias into a UnitOfMeasure.

        Args:
            value: Unit name or abbreviation.

        Returns:
            The matching UnitOfMeasure enum member.

        Raises:
            ValueError: If the unit is not recognized.
        """
        normalized = (
            value.strip()
            .lower()
            .replace(" ", "")
            .replace("_", "")
            .replace("-", "")
        )

        aliases = {
            cls.grams: ["g", "gram", "grams"],
            cls.kilograms: [
                "kg",
                "kilo",
                "kilos",
                "kilogram",
                "kilograms",
            ],
            cls.ounces: ["oz", "ounce", "ounces"],
            cls.pounds: [
                "lb",
                "lbs",
                "pound",
                "pounds",
            ],
            cls.fluid_ounces: [
                "fl oz",
                "floz",
                "fluid ounce",
                "fluid ounces",
                "fluid_ounce",
                "fluid_ounces",
            ],
            cls.milliliters: [
                "ml",
                "milliliter",
                "milliliters",
                "millilitre",
                "millilitres",
            ],
            cls.liters: [
                "l",
                "liter",
                "liters",
                "litre",
                "litres",
            ],
            cls.gallons: [
                "gal",
                "gallon",
                "gallons",
            ],
            cls.pumps: ["pump", "pumps"],
            cls.scoops: ["scoop", "scoops"],
            cls.shots: ["shot", "shots"],
            cls.dashes: ["dash", "dashes"],
        }

        for unit, unit_aliases in aliases.items():
            normalized_aliases = {
                alias.strip()
                .lower()
                .replace(" ", "")
                .replace("_", "")
                .replace("-", "")
                for alias in unit_aliases
            }

            if normalized in normalized_aliases:
                return unit

        raise ValueError(
            f"Unknown unit of measure: {value}"
        )


class CafeAllergen(str, Enum):
    """Supported allergens for cafe ingredients."""

    MILK = "Milk"
    WHEY = "Whey"
    CASEIN = "Casein"
    BUTTER = "Butter"
    CREAM = "Cream"
    EGGS = "Eggs"
    WHEAT = "Wheat"
    BARLEY = "Barley"
    RYE = "Rye"
    OATS = "Oats"
    GLUTEN = "Gluten"
    PEANUTS = "Peanuts"
    ALMONDS = "Almonds"
    CASHEWS = "Cashews"
    WALNUTS = "Walnuts"
    PECANS = "Pecans"
    PISTACHIOS = "Pistachios"
    HAZELNUTS = "Hazelnuts"
    MACADAMIA_NUTS = "Macadamia nuts"
    BRAZIL_NUTS = "Brazil nuts"
    SOY = "Soy"
    SESAME = "Sesame"
    MUSTARD = "Mustard"
    SULFITES = "Sulfites"
    FISH = "Fish"
    SHELLFISH = "Shellfish"
    CRUSTACEANS = "Crustaceans"
    MOLLUSKS = "Mollusks"
    COCONUT = "Coconut"
    LUPIN = "Lupin"
    CELERY = "Celery"
    CORN = "Corn"
    BUCKWHEAT = "Buckwheat"
    SUNFLOWER_SEEDS = "Sunflower seeds"
    PUMPKIN_SEEDS = "Pumpkin seeds"
    POPPY_SEEDS = "Poppy seeds"
    CHICKPEAS = "Chickpeas"
    LENTILS = "Lentils"
    PEAS = "Peas"
    SOY_LECITHIN = "Soy lecithin"
    ALMOND_MILK = "Almond milk"
    SOY_MILK = "Soy milk"
    OAT_MILK = "Oat milk"
    COCONUT_MILK = "Coconut milk"
    TAHINI = "Tahini"
    MARZIPAN = "Marzipan"
    NUT_BASED_PESTO = "Nut-based pesto"
    CHOCOLATE_COCOA = "Chocolate/cocoa"
    CARAMEL = "Caramel coloring or flavorings"
    SHARED_PREPARATION_SURFACES = (
        "Shared fryer or preparation surfaces"
    )

    @classmethod
    def from_string(cls, value: str) -> "CafeAllergen":
        """Convert a string into a CafeAllergen.

        Args:
            value: Allergen name supplied by the caller.

        Returns:
            The matching CafeAllergen enum member.

        Raises:
            ValueError: If the allergen is not recognized.
        """
        normalized = (
            value.strip()
            .lower()
            .replace(" ", "")
            .replace("-", "")
        )

        for allergen in cls:
            allergen_normalized = (
                allergen.value
                .lower()
                .replace(" ", "")
                .replace("-", "")
            )

            if allergen_normalized == normalized:
                return allergen

        raise ValueError(
            f"Unknown allergen: {value}"
        )