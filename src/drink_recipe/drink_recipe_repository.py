from src.ingredient.ingredient_schema import IngredientSchema
from src.constants.DRINK_TYPES import DrinkType
from src.drink_recipe.drink_type_schema import DrinkTypeSchema
from src.drink_recipe.drink_recipe_model import DrinkRecipe
from src.drink_recipe.drink_recipe_schema import DrinkRecipeSchema
from sqlalchemy.orm import Session

def map_enum_to_fk(enum_value: DrinkType, db: Session) -> int:
    drink_type = db.query(DrinkTypeSchema).filter_by(name=enum_value.value).first()
    if not drink_type:
        raise ValueError(f"DrinkType '{enum_value.value}' not found in drink_type table")
    return drink_type.id


class DrinkRecipeRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_drink_recipe(self, drink_recipe: DrinkRecipe) -> DrinkRecipeSchema:
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
        return self.session.query(DrinkRecipeSchema).filter(DrinkRecipeSchema.id == recipe_id).first()

    def get_all_drink_recipes(self) -> list[DrinkRecipeSchema]:
        return self.session.query(DrinkRecipeSchema).all()
