from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from drink_recipe.drink_recipe_response import DrinkRecipeResponse
from drink_recipe.drink_recipe_repository import DrinkRecipeRepository
from drink_recipe.drink_recipe_model import DrinkRecipe

router = APIRouter(
    prefix="/drink_recipes",
    tags=["drink_recipes"]
)


def serialize_recipe(recipe):
    """Shared serializer for DrinkRecipeResponse."""
    return {
        "id": recipe.id,
        "name": recipe.name,
        "description": recipe.description,
        "active": recipe.active,
        "type": recipe.drink_type.name,
        "ingredients": [
            {
                "id": assoc.ingredient.id,
                "name": assoc.ingredient.name,
                "quantity_used": assoc.quantity_used,
                "unit_of_measure_used": assoc.unit_of_measure_used,
            }
            for assoc in recipe.recipe_ingredients
        ],
        "production_cost": recipe.production_cost,
        "markup_percentage": recipe.markup_percentage,
        "sale_price": recipe.sale_price,
    }


@router.post("/", response_model=DrinkRecipeResponse)
def create_drink_recipe(drink_recipe: DrinkRecipe, db: Session = Depends(get_db)):
    repo = DrinkRecipeRepository(db)
    recipe = repo.create_drink_recipe(drink_recipe)
    return DrinkRecipeResponse.model_validate(serialize_recipe(recipe))


@router.get("/{recipe_id}", response_model=DrinkRecipeResponse)
def get_drink_recipe(recipe_id: int, db: Session = Depends(get_db)):
    repo = DrinkRecipeRepository(db)
    recipe = repo.get_drink_recipe_by_id(recipe_id)

    if not recipe:
        raise HTTPException(status_code=404, detail="Drink recipe not found")

    return DrinkRecipeResponse.model_validate(serialize_recipe(recipe))


@router.get("/", response_model=list[DrinkRecipeResponse])
def get_all_drink_recipes(db: Session = Depends(get_db)):
    repo = DrinkRecipeRepository(db)
    recipes = repo.get_all_drink_recipes()

    return [
        DrinkRecipeResponse.model_validate(serialize_recipe(r))
        for r in recipes
    ]
