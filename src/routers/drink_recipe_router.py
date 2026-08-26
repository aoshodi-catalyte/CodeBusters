"""
API router for drink recipe operations.

This module defines the HTTP endpoints used to create and retrieve drink
recipes. It acts as the presentation layer of the drink recipe system,
coordinating request validation, repository interaction, and response
serialization.

Endpoints:
    • POST /drink_recipes/
        Create a new drink recipe, including ingredient usage, production
        cost calculation, markup application, and sale price generation.

    • GET /drink_recipes/{recipe_id}
        Retrieve a single drink recipe by its ID. Returns full recipe
        details including ingredients, pricing, and drink type.

    • GET /drink_recipes/
        Retrieve all drink recipes stored in the database.

The router uses:
    • DrinkRecipe (Pydantic) for request validation
    • DrinkRecipeRepository for database operations and cost computation
    • DrinkRecipeResponse (Pydantic) for structured API responses

A shared serializer function converts ORM models into dictionaries that
are validated through DrinkRecipeResponse before being returned to clients.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_db
from drink_recipe.drink_recipe_model import DrinkRecipe
from drink_recipe.drink_recipe_response import DrinkRecipeResponse
from exceptions.drink_recipe_exceptions import (
    DrinkTypeNotFoundError,
    DuplicateDrinkRecipeNameError,
    IngredientNotFoundError,
    UnitConversionError,
)
from repositories.drink_recipe_repository import DrinkRecipeRepository
from utils.response import to_response

router = APIRouter(
    prefix="/drink_recipes",
    tags=["drink_recipes"]
)


def serialize_recipe(recipe):
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


@router.post("/", response_model=DrinkRecipeResponse, status_code=201)
def create_drink_recipe(drink_recipe: DrinkRecipe, db: Session = Depends(get_db)):
    repo = DrinkRecipeRepository(db)

    try:
        recipe = repo.create_drink_recipe(drink_recipe)
        return to_response(DrinkRecipeResponse, serialize_recipe(recipe))

    # --- Domain exceptions mapped to HTTP responses ---
    except DrinkTypeNotFoundError as e:
        db.rollback()
        raise HTTPException(status_code=404, detail=str(e)) from e

    except DuplicateDrinkRecipeNameError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail=str(e)) from e

    except IngredientNotFoundError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail=str(e)) from e

    except UnitConversionError as e:
        db.rollback()
        raise HTTPException(status_code=422, detail=str(e)) from e

    # --- SQLAlchemy constraint errors ---
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail=f"Drink recipe name '{drink_recipe.name}' already exists"
        ) from e

    # --- Catch-all fallback ---
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while creating the drink recipe."
        ) from e


@router.get("/{recipe_id}", response_model=DrinkRecipeResponse)
def get_drink_recipe(recipe_id: int, db: Session = Depends(get_db)):
    repo = DrinkRecipeRepository(db)
    recipe = repo.get_drink_recipe_by_id(recipe_id)

    if not recipe:
        raise HTTPException(status_code=404, detail="Drink recipe not found")

    return to_response(DrinkRecipeResponse, serialize_recipe(recipe))


@router.get("/", response_model=list[DrinkRecipeResponse])
def get_all_drink_recipes(db: Session = Depends(get_db)):
    repo = DrinkRecipeRepository(db)
    recipes = repo.get_all_drink_recipes()

    return [
        to_response(DrinkRecipeResponse, serialize_recipe(recipe))
        for recipe in recipes
    ]
