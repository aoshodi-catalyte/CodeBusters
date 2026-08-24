"""
Association table linking drink recipes to the specific ingredients they use.

    This model represents a single ingredient usage entry within a drink recipe.
    It enables a many‑to‑many relationship between DrinkRecipeSchema and
    IngredientSchema, while also storing recipe‑specific usage details such as
    quantity and unit of measurement.

    Each row describes:
        • which recipe the ingredient belongs to
        • which ingredient is being used
        • how much of the ingredient the recipe requires
        • the unit in which that quantity is measured
"""

from sqlalchemy import Column, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship
from database import Base


class DrinkRecipeIngredientSchema(Base):
    """
    Fields:
        id (int):
            Primary key for the association record.

        drink_recipe_id (int):
            Foreign key referencing the drink recipe that uses the ingredient.

        ingredient_id (int):
            Foreign key referencing the ingredient being used.

        quantity_used (Numeric):
            The amount of the ingredient required for the recipe. Stored as a
            numeric value with two decimal places.

        unit_of_measure_used (str):
            The unit describing how the recipe measures the ingredient
            (e.g., "oz", "g", "ml"). This may differ from the ingredient's
            purchase unit and is used during cost conversion.

    Relationships:
        drink_recipe:
            SQLAlchemy relationship to DrinkRecipeSchema, allowing navigation
            from an ingredient usage entry back to its recipe.

        ingredient:
            SQLAlchemy relationship to IngredientSchema, allowing access to
            ingredient details such as name, cost, and purchase unit.
    """

    __tablename__ = "drink_recipe_ingredient"

    id = Column(Integer, primary_key=True, index=True)

    drink_recipe_id = Column(Integer, ForeignKey("drink_recipe.id"), nullable=False)
    ingredient_id = Column(Integer, ForeignKey("ingredient.id"), nullable=False)

    # NEW: recipe-specific usage fields
    quantity_used = Column(Numeric(10, 2), nullable=False)
    unit_of_measure_used = Column(String(50), nullable=False)

    drink_recipe = relationship("DrinkRecipeSchema", back_populates="recipe_ingredients")
    ingredient = relationship("IngredientSchema", back_populates="ingredient_recipes")