"""
FastAPI router for drink recipe endpoints.

This module defines the API routes for managing drink recipes. It provides
endpoints for creating new drink recipes, retrieving recipes by ID, and
fetching all available recipes. All endpoints handle the conversion between
the Pydantic data models and database ORM models.
"""

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


@router.post("/", response_model=DrinkRecipeResponse)
def create_drink_recipe(drink_recipe: DrinkRecipe, db: Session = Depends(get_db)):
    """
    Create a new drink recipe.

    Creates a new drink recipe in the database with the provided details,
    including name, description, pricing information, and associated ingredients.
    The endpoint validates the drink type and ingredient IDs before persisting
    the recipe.

    Args:
        drink_recipe: The DrinkRecipe model containing recipe details and ingredient IDs.
        db: SQLAlchemy database session (injected via Depends).

    Returns:
        DrinkRecipeResponse: The created drink recipe with its assigned database ID
            and all related information formatted for API response.

    Raises:
        HTTPException: If the drink type is invalid or ingredients are not found.
    """
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
    """
    Retrieve a specific drink recipe by its ID.

    Fetches a drink recipe from the database using its unique identifier.
    The response includes all recipe details and associated ingredients.

    Args:
        recipe_id: The unique identifier of the drink recipe to retrieve.
        db: SQLAlchemy database session (injected via Depends).

    Returns:
        DrinkRecipeResponse: The requested drink recipe with all its details
            and associated ingredients.

    Raises:
        HTTPException: 404 error if the drink recipe with the given ID is not found.
    """
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
    """
    Retrieve all drink recipes.

    Fetches a list of all drink recipes currently stored in the database.
    Each recipe includes all its details and associated ingredients.

    Args:
        db: SQLAlchemy database session (injected via Depends).

    Returns:
        list[DrinkRecipeResponse]: A list of all drink recipes. Returns an empty
            list if no recipes exist in the database.
    """
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
