from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from drink_recipe.drink_recipe_repository import DrinkRecipeRepository
from drink_recipe.drink_recipe_schema import DrinkRecipeSchema
from drink_recipe.drink_recipe_model import DrinkRecipe
from database import get_db

router = APIRouter(
    prefix="/drink_recipes", 
    tags=["drink_recipes"]
)

@router.post("/", response_model=DrinkRecipeSchema)
def create_drink_recipe(drink_recipe: DrinkRecipe, db: Session = Depends(get_db)):
    repository = DrinkRecipeRepository(db)
    return repository.create_drink_recipe(drink_recipe)

@router.get("/{recipe_id}", response_model=DrinkRecipeSchema)
def get_drink_recipe(recipe_id: int, db: Session = Depends(get_db)):
    repository = DrinkRecipeRepository(db)
    drink_recipe = repository.get_drink_recipe_by_id(recipe_id)
    if not drink_recipe:
        raise HTTPException(status_code=404, detail="Drink recipe not found")
    return drink_recipe

@router.get("/", response_model=list[DrinkRecipeSchema])
def get_all_drink_recipes(db: Session = Depends(get_db)):
    repository = DrinkRecipeRepository(db)
    return repository.get_all_drink_recipes()