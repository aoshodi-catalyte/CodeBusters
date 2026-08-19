"""Constants and enums used for ingredient validation."""

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
        """Convert a string or alias into a UnitOfMeasure enum value.

        Args:
            value: Unit name or abbreviation supplied by the user.

        Returns:
            The matching UnitOfMeasure enum member.

        Raises:
            ValueError: If the supplied value is not a recognized unit.
        """
        normalized = cls._normalize(value)

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
            cls.pounds: ["lb", "lbs", "pound", "pounds"],
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
            cls.gallons: ["gal", "gallon", "gallons"],
            cls.pumps: ["pump", "pumps"],
            cls.scoops: ["scoop", "scoops"],
            cls.shots: ["shot", "shots"],
            cls.dashes: ["dash", "dashes"],
        }

        for unit, unit_aliases in aliases.items():
            normalized_aliases = {
                cls._normalize(alias)
                for alias in unit_aliases
            }

            if normalized in normalized_aliases:
                return unit

        raise ValueError(f"Unknown unit of measure: {value}")

    @staticmethod
    def _normalize(value: str) -> str:
        """Normalize a unit string for comparison.

        Args:
            value: Unit string to normalize.

        Returns:
            Normalized unit string.
        """
        return (
            value.strip()
            .lower()
            .replace(" ", "")
            .replace("_", "")
            .replace("-", "")
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
        """Convert a string into a CafeAllergen enum value.

        Args:
            value: Allergen name supplied by the user.

        Returns:
            The matching CafeAllergen enum member.

        Raises:
            ValueError: If the supplied value is not a recognized
                allergen.
        """
        normalized = cls._normalize(value)

        for allergen in cls:
            allergen_normalized = cls._normalize(allergen.value)

            if allergen_normalized == normalized:
                return allergen

        raise ValueError(f"Unknown allergen: {value}")

    @staticmethod
    def _normalize(value: str) -> str:
        """Normalize an allergen string for comparison.

        Args:
            value: Allergen string to normalize.

        Returns:
            Normalized allergen string.
        """
        return (
            value.strip()
            .lower()
            .replace(" ", "")
            .replace("-", "")
        )