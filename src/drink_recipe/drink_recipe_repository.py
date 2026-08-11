from drink_recipe_model import DrinkRecipe
from drink_recipe_schema import DrinkRecipeSchema
from sqlalchemy.orm import Session

class DrinkRecipeRepository:
    def __init__(self, session: Session):
        self.session: Session = session

    def create_drink_recipe(self, drink_recipe: DrinkRecipe) -> DrinkRecipeSchema:
        drink_recipe_schema = DrinkRecipeSchema(
            name=drink_recipe.name,
            description=drink_recipe.description,
            active=drink_recipe.active,
            type=drink_recipe.type.value,
            production_cost=float(drink_recipe.production_cost),
        )
        self.session.add(drink_recipe_schema)
        self.session.commit()
        self.session.refresh(drink_recipe_schema)
        return drink_recipe_schema

    def get_drink_recipe_by_id(self, recipe_id: int) -> DrinkRecipeSchema | None:
        return self.session.query(DrinkRecipeSchema).filter(DrinkRecipeSchema.id == recipe_id).first()

    def get_all_drink_recipes(self) -> list[DrinkRecipeSchema]:
        return self.session.query(DrinkRecipeSchema).all()