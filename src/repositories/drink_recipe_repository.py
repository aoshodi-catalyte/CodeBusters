"""
Repository responsible for creating, retrieving, and managing drink recipe
records in the database.

This class encapsulates all persistence and data-access logic for drink
recipes. It coordinates ingredient lookup, unit conversion, cost calculation,
markup application, and association table creation. The repository ensures
that incoming DrinkRecipe models are transformed into fully populated
DrinkRecipeSchema ORM objects with accurate production cost and sale price.

Responsibilities:
    • Validate and resolve the drink type enum into its database ID.
    • Create new drink recipe records and persist them to the database.
    • Convert recipe ingredient usage units into the ingredient's purchase
      unit using the unit conversion system.
    • Calculate production cost by summing the cost contribution of each
      ingredient based on purchasing cost and converted usage amount.
    • Apply markup percentage to compute the final sale price.
    • Create association records linking recipes to their ingredient usage.
    • Retrieve individual drink recipes by ID.
    • Retrieve all drink recipes stored in the database.
"""

import re

from sqlalchemy import func
from sqlalchemy.orm import Session

from constants.drink_types import DrinkType
from constants.unit_conversions import convert
from drink_recipe.drink_ingredients_schema import DrinkRecipeIngredientSchema
from drink_recipe.drink_recipe_model import DrinkRecipe
from drink_recipe.drink_recipe_schema import DrinkRecipeSchema
from drink_recipe.drink_type_schema import DrinkTypeSchema
from exceptions.drink_recipe_exceptions import (
    DrinkRecipeAlreadyDeacivated,
    DrinkRecipeNotFoundError,
    DrinkTypeNotFoundError,
    DuplicateDrinkRecipeNameError,
    IngredientNotFoundError,
    UnitConversionError,
)
from ingredient.ingredient_schema import IngredientSchema
from utils.validators import round_float


def map_enum_to_fk(enum_value: DrinkType, db: Session) -> int:
    """
    Map a DrinkType enum to its corresponding foreign key ID in the database.
    """
    drink_type = db.query(DrinkTypeSchema).filter_by(name=enum_value.value).first()
    if not drink_type:
        raise DrinkTypeNotFoundError(enum_value.value)
    return drink_type.id


class DrinkRecipeRepository:
    """
    Repository responsible for creating, retrieving, and managing drink recipe records.
    """
    def __init__(self, session: Session):
        self.session = session

    def _normalize_name(self, name: str) -> str:
        """
        Normalize a drink recipe name for duplicate detection.

        Removes all whitespace and lowercases the string so that
        names like "Iced Latte" and "iced   latte" are treated
        as identical during uniqueness checks.

        Returns:
            str: Normalized name string.
        """
        return re.sub(r"\s+", "", name).lower()

    def _ensure_name_unique(self, name: str, exclude_id: int | None = None) -> None:
        """
        Ensure that a drink recipe name does not already exist.

        Performs normalized name comparison to detect duplicates.
        Optionally excludes a specific recipe ID (used during updates).

        Args:
            name (str): The proposed recipe name.
            exclude_id (int | None): A recipe ID to ignore during lookup.

        Raises:
            DuplicateDrinkRecipeNameError: If another recipe already uses the name.
        """
        normalized = self._normalize_name(name)

        query = self.session.query(DrinkRecipeSchema).filter(
            func.lower(func.replace(DrinkRecipeSchema.name, " ", "")) == normalized
        )

        if exclude_id is not None:
            query = query.filter(DrinkRecipeSchema.id != exclude_id)

        if query.first():
            raise DuplicateDrinkRecipeNameError(name)

    def _process_ingredients(self, ingredients):
        """
        Validate ingredients and compute total production cost.

        Args:
            ingredients (list[DrinkIngredient]): Incoming ingredient usage models.

        Returns:
            tuple[list[dict], float]:
                • A list of validated ingredient dictionaries.
                • The total production cost for the recipe.

        Raises:
            IngredientNotFoundError: If an ingredient ID does not exist.
            UnitConversionError: If unit conversion fails.
        """
        validated = []
        total_cost = 0.0

        for ing in ingredients:
            ingredient = self.session.get(IngredientSchema, ing.id)
            if not ingredient:
                raise IngredientNotFoundError(ing.id)

            try:
                converted_amount = convert(
                    ing.quantity_used,
                    ing.unit_of_measure_used,
                    ingredient.unit_of_measure,
                )
            except ValueError as e:
                raise UnitConversionError(ingredient.name, str(e)) from e

            cost_per_unit = ingredient.purchasing_cost / ingredient.unit_amount
            ingredient_cost = float(cost_per_unit) * float(converted_amount)
            total_cost += ingredient_cost

            validated.append(
                {
                    "ingredient_id": ingredient.id,
                    "quantity_used": ing.quantity_used,
                    "unit_of_measure_used": ing.unit_of_measure_used,
                }
            )

        return validated, total_cost

    def _apply_ingredients(self, recipe_id: int, validated_ingredients):
        """
        Replace all ingredient associations for a recipe.

        Deletes existing DrinkRecipeIngredientSchema rows for the recipe
        and inserts new association records based on validated ingredient data.

        Args:
            recipe_id (int): The recipe being updated.
            validated_ingredients (list[dict]): Ingredient usage payloads.
        """
        self.session.query(DrinkRecipeIngredientSchema).filter(
            DrinkRecipeIngredientSchema.drink_recipe_id == recipe_id
        ).delete()

        for ing in validated_ingredients:
            assoc = DrinkRecipeIngredientSchema(
                drink_recipe_id=recipe_id,
                ingredient_id=ing["ingredient_id"],
                quantity_used=ing["quantity_used"],
                unit_of_measure_used=ing["unit_of_measure_used"],
            )
            self.session.add(assoc)

    def _apply_costs(self, recipe: DrinkRecipeSchema, total_cost: float):
        """
        Apply production cost and sale price to a recipe.

        Production cost is rounded using the validator system.
        Sale price is computed using markup percentage:
            sale_price = production_cost * (1 + markup_percentage/100)

        Args:
            recipe (DrinkRecipeSchema): The ORM recipe object to update.
            total_cost (float): The computed production cost.
        """
        recipe.production_cost = round_float(total_cost)
        markup_multiplier = 1 + (recipe.markup_percentage / 100)
        recipe.sale_price = round_float(recipe.production_cost * markup_multiplier)


    def create_drink_recipe(self, drink_recipe: DrinkRecipe) -> DrinkRecipeSchema:
        """
        Create a new drink recipe, calculate its costs,
        persist it, and return the ORM representation.
        """
        self._ensure_name_unique(drink_recipe.name)

        recipe = DrinkRecipeSchema(
            name=drink_recipe.name,
            description=drink_recipe.description,
            active=drink_recipe.active,
            type_id=map_enum_to_fk(drink_recipe.type, self.session),
            markup_percentage=drink_recipe.markup_percentage,
        )

        self.session.add(recipe)
        self.session.flush()

        validated_ingredients, total_cost = self._process_ingredients(
            drink_recipe.ingredients
        )

        self._apply_ingredients(recipe.id, validated_ingredients)
        self._apply_costs(recipe, total_cost)

        self.session.commit()
        self.session.refresh(recipe)
        return recipe


    def get_drink_recipe_by_id(self, recipe_id: int) -> DrinkRecipeSchema:
        """
        Retrieve a drink recipe by its ID.
        """
        recipe = (
            self.session.query(DrinkRecipeSchema)
            .filter(DrinkRecipeSchema.id == recipe_id)
            .first()
        )

        if not recipe:
            raise DrinkRecipeNotFoundError(recipe_id)

        return recipe


    def get_all_drink_recipes(self) -> list[DrinkRecipeSchema]:
        """
        Retrieve all drink recipes.
        """
        return self.session.query(DrinkRecipeSchema).all()


    def update_drink_recipe_by_id(
        self,
        recipe_id: int,
        drink_recipe_data: DrinkRecipe
        ) -> DrinkRecipeSchema:
        """
        Update a drink recipe by its ID.
        """

        recipe = self.get_drink_recipe_by_id(recipe_id)

        self._ensure_name_unique(drink_recipe_data.name, exclude_id=recipe_id)

        validated_ingredients, total_cost = self._process_ingredients(
            drink_recipe_data.ingredients
        )

        recipe.name = drink_recipe_data.name
        recipe.description = drink_recipe_data.description
        recipe.active = drink_recipe_data.active
        recipe.type_id = map_enum_to_fk(drink_recipe_data.type, self.session)
        recipe.markup_percentage = drink_recipe_data.markup_percentage

        self._apply_ingredients(recipe.id, validated_ingredients)
        self._apply_costs(recipe, total_cost)

        self.session.commit()
        self.session.refresh(recipe)
        return recipe


    def deactivate_drink_recipe_by_id(self, recipe_id: int) -> DrinkRecipeSchema:
        """
        Set a drink recipe's status to false by its ID.
        """
        recipe = self.get_drink_recipe_by_id(recipe_id)

        # Check if drink status is already set to false
        if recipe.active is False:
            raise DrinkRecipeAlreadyDeacivated(recipe.name)

        recipe.active = False

        self.session.commit()
        self.session.refresh(recipe)
        return recipe
