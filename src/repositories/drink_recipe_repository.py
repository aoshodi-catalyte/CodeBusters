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

    def create_drink_recipe(self, drink_recipe: DrinkRecipe) -> DrinkRecipeSchema:
        """
        Create a new drink recipe, calculate its costs,
        persist it, and return the ORM representation.
        """
        drink_type_id = map_enum_to_fk(drink_recipe.type, self.session)

        # Normalize name for duplicate detection
        normalized_input = re.sub(r"\s+", "", drink_recipe.name).lower()

        existing = (
            self.session.query(DrinkRecipeSchema)
            .filter(
                func.lower(func.replace(DrinkRecipeSchema.name, " ", ""))
                == normalized_input
            )
            .first()
        )

        if existing:
            raise DuplicateDrinkRecipeNameError(drink_recipe.name)

        recipe = DrinkRecipeSchema(
            name=drink_recipe.name,
            description=drink_recipe.description,
            active=drink_recipe.active,
            type_id=drink_type_id,
            markup_percentage=drink_recipe.markup_percentage,
        )

        self.session.add(recipe)
        self.session.flush()

        total_cost = 0.00

        for ing in drink_recipe.ingredients:
            ingredient = self.session.get(IngredientSchema, ing.id)
            if not ingredient:
                raise IngredientNotFoundError(ing.id)

            # Convert recipe usage → ingredient purchase unit
            try:
                recipe_amount_in_purchase_unit = convert(
                    ing.quantity_used,
                    ing.unit_of_measure_used,
                    ingredient.unit_of_measure,
                )
            except ValueError as e:
                raise UnitConversionError(ingredient.name, str(e)) from e

            # Cost per unit of ingredient
            cost_per_unit = ingredient.purchasing_cost / ingredient.unit_amount

            # Cost for this ingredient in the recipe
            ingredient_cost = float(cost_per_unit) * float(
                recipe_amount_in_purchase_unit
            )
            total_cost += ingredient_cost

            assoc = DrinkRecipeIngredientSchema(
                drink_recipe_id=recipe.id,
                ingredient_id=ingredient.id,
                quantity_used=ing.quantity_used,
                unit_of_measure_used=ing.unit_of_measure_used,
            )
            self.session.add(assoc)

        # Assign calculated production cost
        recipe.production_cost = round_float(total_cost)

        # Calculate sale price
        markup_multiplier = 1 + (recipe.markup_percentage / 100)
        recipe.sale_price = round_float(recipe.production_cost * markup_multiplier)

        self.session.commit()
        self.session.refresh(recipe)
        return recipe

    def get_drink_recipe_by_id(self, recipe_id: int) -> DrinkRecipeSchema | None:
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

        # Normalize name for duplicate detection
        normalized_input = re.sub(r"\s+", "", drink_recipe_data.name).lower()

        existing = (
            self.session.query(DrinkRecipeSchema)
            .filter(
                func.lower(func.replace(DrinkRecipeSchema.name, " ", "")) == normalized_input,
                DrinkRecipeSchema.id != recipe_id
            )
            .first()
        )

        if existing:
            raise DuplicateDrinkRecipeNameError(drink_recipe_data.name)

        # Update basic fields
        recipe.name = drink_recipe_data.name
        recipe.description = drink_recipe_data.description
        recipe.active = drink_recipe_data.active
        recipe.type_id = map_enum_to_fk(drink_recipe_data.type, self.session)
        recipe.markup_percentage = drink_recipe_data.markup_percentage

        # Remove old ingredient associations
        self.session.query(DrinkRecipeIngredientSchema).filter(
            DrinkRecipeIngredientSchema.drink_recipe_id == recipe.id
        ).delete()

        total_cost = 0.0

        # Rebuild ingredient associations
        for ing in drink_recipe_data.ingredients:
            ingredient = self.session.get(IngredientSchema, ing.id)
            if not ingredient:
                raise IngredientNotFoundError(ing.id)

            try:
                recipe_amount_in_purchase_unit = convert(
                    ing.quantity_used,
                    ing.unit_of_measure_used,
                    ingredient.unit_of_measure,
                )
            except ValueError as e:
                raise UnitConversionError(ingredient.name, str(e)) from e

            cost_per_unit = ingredient.purchasing_cost / ingredient.unit_amount
            ingredient_cost = float(cost_per_unit) * float(recipe_amount_in_purchase_unit)
            total_cost += ingredient_cost

            assoc = DrinkRecipeIngredientSchema(
                drink_recipe_id=recipe.id,
                ingredient_id=ingredient.id,
                quantity_used=ing.quantity_used,
                unit_of_measure_used=ing.unit_of_measure_used,
            )
            self.session.add(assoc)

        recipe.production_cost = round_float(total_cost)
        markup_multiplier = 1 + (recipe.markup_percentage / 100)
        recipe.sale_price = round_float(recipe.production_cost * markup_multiplier)

        self.session.commit()
        self.session.refresh(recipe)
        return recipe
