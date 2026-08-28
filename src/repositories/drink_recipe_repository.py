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
    drink_type = db.query(DrinkTypeSchema).filter_by(name=enum_value.value).first()
    if not drink_type:
        raise DrinkTypeNotFoundError(enum_value.value)
    return drink_type.id


class DrinkRecipeRepository:
    def __init__(self, session: Session):
        self.session = session

    def _normalize_name(self, name: str) -> str:
        return re.sub(r"\s+", "", name).lower()

    def _ensure_name_unique(self, name: str, exclude_id: int | None = None) -> None:
        normalized = self._normalize_name(name)

        query = self.session.query(DrinkRecipeSchema).filter(
            func.lower(func.replace(DrinkRecipeSchema.name, " ", "")) == normalized
        )

        if exclude_id is not None:
            query = query.filter(DrinkRecipeSchema.id != exclude_id)

        if query.first():
            raise DuplicateDrinkRecipeNameError(name)

    def _process_ingredients(self, ingredients):
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
        recipe.production_cost = round_float(total_cost)
        markup_multiplier = 1 + (recipe.markup_percentage / 100)
        recipe.sale_price = round_float(recipe.production_cost * markup_multiplier)


    def create_drink_recipe(self, drink_recipe: DrinkRecipe) -> DrinkRecipeSchema:
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
        recipe = (
            self.session.query(DrinkRecipeSchema)
            .filter(DrinkRecipeSchema.id == recipe_id)
            .first()
        )

        if not recipe:
            raise DrinkRecipeNotFoundError(recipe_id)

        return recipe


    def get_all_drink_recipes(self) -> list[DrinkRecipeSchema]:
        return self.session.query(DrinkRecipeSchema).all()


    def update_drink_recipe_by_id(self, recipe_id: int, drink_recipe_data: DrinkRecipe) -> DrinkRecipeSchema:

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
