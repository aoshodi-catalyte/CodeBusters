"""
Repository layer for drink recipe data access and manipulation.

This module provides the DrinkRecipeRepository class which handles all database
operations related to drink recipes, including creation, retrieval, and ingredient
association. It also includes a utility function for mapping drink type enums
to their corresponding database IDs.
"""

from ingredient.ingredient_schema import IngredientSchema
from constants.DRINK_TYPES import DrinkType
from drink_recipe.drink_type_schema import DrinkTypeSchema
from drink_recipe.drink_recipe_model import DrinkRecipe
from drink_recipe.drink_recipe_schema import DrinkRecipeSchema
from sqlalchemy.orm import Session


def map_enum_to_fk(enum_value: DrinkType, db: Session) -> int:
    """
    Map a DrinkType enum to its corresponding foreign key ID in the database.

    Looks up the drink type in the database by name and returns its ID.
    This function bridges the gap between the application's DrinkType enum
    and the database's drink_type table.

    Args:
        enum_value: The DrinkType enum value to look up.
        db: SQLAlchemy session for database queries.

    Returns:
        The ID of the drink type in the drink_type table.

    Raises:
        ValueError: If the drink type is not found in the database.
    """
    drink_type = db.query(DrinkTypeSchema).filter_by(name=enum_value.value).first()
    if not drink_type:
        raise ValueError(f"DrinkType '{enum_value.value}' not found in drink_type table")
    return drink_type.id


class DrinkRecipeRepository:
    """
    Repository for managing drink recipe data access and persistence.

    This class provides methods to perform CRUD operations on drink recipes,
    including creating new recipes with associated ingredients and retrieving
    recipes from the database. It works with the DrinkRecipeSchema ORM model
    and handles the mapping between Pydantic models and database entities.

    Attributes:
        session: SQLAlchemy ORM session for database operations.
    """

    def __init__(self, session: Session):
        """
        Initialize the repository with a database session.

        Args:
            session: SQLAlchemy ORM session for database operations.
        """
        self.session = session

    def create_drink_recipe(self, drink_recipe: DrinkRecipe) -> DrinkRecipeSchema:
        """
        Create a new drink recipe with associated ingredients.

        Creates a new drink recipe in the database, associates it with the
        specified ingredients, and returns the created recipe with its ID.
        The drink type enum is converted to its corresponding database ID.

        Args:
            drink_recipe: The DrinkRecipe model containing recipe details and ingredient IDs.

        Returns:
            The created DrinkRecipeSchema object with the database ID populated.

        Raises:
            ValueError: If the drink type is not found in the database.
        """
        drink_type_id = map_enum_to_fk(drink_recipe.type, self.session)

        recipe = DrinkRecipeSchema(
            name=drink_recipe.name,
            description=drink_recipe.description,
            active=drink_recipe.active,
            type_id=drink_type_id,
            production_cost=drink_recipe.production_cost,
            markup_percentage=drink_recipe.markup_percentage,
            sale_price=drink_recipe.sale_price,
        )

        self.session.add(recipe)
        self.session.flush()

        for ingredient_id in drink_recipe.ingredients:
            ingredient = self.session.get(IngredientSchema, ingredient_id)
            if ingredient:
                recipe.ingredients.append(ingredient)

        self.session.commit()
        self.session.refresh(recipe)
        return recipe

    def get_drink_recipe_by_id(self, recipe_id: int) -> DrinkRecipeSchema | None:
        """
        Retrieve a drink recipe by its ID.

        Queries the database for a drink recipe with the specified ID.

        Args:
            recipe_id: The unique identifier of the drink recipe.

        Returns:
            The DrinkRecipeSchema object if found, None otherwise.
        """
        return self.session.query(DrinkRecipeSchema).filter(DrinkRecipeSchema.id == recipe_id).first()

    def get_all_drink_recipes(self) -> list[DrinkRecipeSchema]:
        """
        Retrieve all drink recipes from the database.

        Queries and returns all drink recipes currently stored in the database.

        Returns:
            A list of all DrinkRecipeSchema objects in the database. Returns an
            empty list if no recipes exist.
        """
        return self.session.query(DrinkRecipeSchema).all()
