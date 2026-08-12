from typing import Generator
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import engine
from sqlalchemy.orm import Session
from drink_recipe.drink_recipe_response import DrinkRecipeResponse
from database import get_db
from drink_recipe.drink_recipe_repository import DrinkRecipeRepository
from drink_recipe.drink_recipe_model import DrinkRecipe


router = APIRouter(
    prefix="/drink_recipes", 
    tags=["drink_recipes"]
)

@router.post("/", response_model=DrinkRecipeResponse)
def create_drink_recipe(drink_recipe: DrinkRecipe, db: Session = Depends(get_db)):
    repo = DrinkRecipeRepository(db)
    recipe = repo.create_drink_recipe(drink_recipe)

    return DrinkRecipeResponse.model_validate({
        "id": recipe.id,
        "name": recipe.name,
        "description": recipe.description,
        "active": recipe.active,
        "type": recipe.drink_type.name,
        "ingredients": [
            {"id": i.id, "name": i.name} for i in recipe.ingredients
        ],
        "production_cost": recipe.production_cost,
        "markup_percentage": recipe.markup_percentage,
        "sale_price": recipe.sale_price,
    })


@router.get("/{recipe_id}", response_model=DrinkRecipeResponse)
def get_drink_recipe(recipe_id: int, db: Session = Depends(get_db)):
    repository = DrinkRecipeRepository(db)
    r = repository.get_drink_recipe_by_id(recipe_id)
    if not r:
        raise HTTPException(status_code=404, detail="Drink recipe not found")

    return DrinkRecipeResponse.model_validate({
        "id": r.id,
        "name": r.name,
        "description": r.description,
        "active": r.active,
        "type": r.drink_type.name,
        "ingredients": [
            {"id": i.id, "name": i.name} for i in r.ingredients
        ],
        "production_cost": r.production_cost,
        "markup_percentage": r.markup_percentage,
        "sale_price": r.sale_price,
    })


@router.get("/", response_model=list[DrinkRecipeResponse])
def get_all_drink_recipes(db: Session = Depends(get_db)):
    repository = DrinkRecipeRepository(db)
    recipes = repository.get_all_drink_recipes()

    return [
        DrinkRecipeResponse.model_validate({
            "id": r.id,
            "name": r.name,
            "description": r.description,
            "active": r.active,
            "type": r.drink_type.name,
            "ingredients": [
                {"id": i.id, "name": i.name} for i in r.ingredients
            ],
            "production_cost": r.production_cost,
            "markup_percentage": r.markup_percentage,
            "sale_price": r.sale_price,
        })
        for r in recipes
    ]
