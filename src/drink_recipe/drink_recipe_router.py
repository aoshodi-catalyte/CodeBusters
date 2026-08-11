from typing import Generator
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import engine
from sqlalchemy.orm import Session
from src.database import SessionLocal, engine, Base
from src.drink_recipe.drink_recipe_repository import DrinkRecipeRepository
from src.drink_recipe.drink_recipe_schema import DrinkRecipeSchema
from src.drink_recipe.drink_recipe_model import DrinkRecipe


Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

router = APIRouter(
    prefix="/drink_recipes", 
    tags=["drink_recipes"]
)

def get_db() -> Generator[Session, None, None]:
    """Provide a SQLAlchemy session for the duration of a request.

    Yields:
        A database session that is closed when the request completes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=DrinkRecipe)
def create_drink_recipe(drink_recipe: DrinkRecipe, db: Session = Depends(get_db)):
    repository = DrinkRecipeRepository(db)
    return repository.create_drink_recipe(drink_recipe)

@router.get("/{recipe_id}", response_model=DrinkRecipe)
def get_drink_recipe(recipe_id: int, db: Session = Depends(get_db)):
    repository = DrinkRecipeRepository(db)
    drink_recipe = repository.get_drink_recipe_by_id(recipe_id)
    if not drink_recipe:
        raise HTTPException(status_code=404, detail="Drink recipe not found")
    return drink_recipe

@router.get("/", response_model=list[DrinkRecipe])
def get_all_drink_recipes(db: Session = Depends(get_db)):
    repository = DrinkRecipeRepository(db)
    return repository.get_all_drink_recipes()