from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from ingredient.ingredient_model import Ingredient
from ingredient.ingredient_schema import AllergenSchema, IngredientSchema
from vendor.vendor_schema import Vendor

class VendorNotFoundError(Exception):
    pass

def get_or_create_allergen(
    db: Session,
    allergen_name: str,
):
    # Find an existing allergen by name
    allergen = (
        db.query(AllergenSchema)
        .filter(AllergenSchema.name == allergen_name)
        .first()
    )
    # If the allergen does not exist, create it
    if allergen is None:
        allergen = AllergenSchema(
            name=allergen_name
        )
        db.add(allergen)
        db.flush()
    return allergen

def create_ingredient(
    db: Session,
    ingredient_data: Ingredient,
):
    try:
        # Check vendor exists
        vendor = (
            db.query(Vendor)
            .filter(Vendor.id == ingredient_data.vendor_id)
            .first()
        )
        if vendor is None:
            raise VendorNotFoundError(
                f"Vendor with ID {ingredient_data.vendor_id} does not exist."
            )
        # Remove duplicate allergens
        unique_allergens = list(
            dict.fromkeys(ingredient_data.allergens)
        )
        # Create the SQLAlchemy ingredient (Pydantic Validation)
        ingredient = IngredientSchema(
            active=ingredient_data.active,
            name=ingredient_data.name,
            purchasing_cost=ingredient_data.purchasing_cost,
            unit_amount=ingredient_data.unit_amount,
            unit_of_measure=ingredient_data.unit_of_measure,
            vendor_id=ingredient_data.vendor_id,
        )
        # Find or create each allergen
        for allergen_name in unique_allergens:
            allergen = get_or_create_allergen(
                db=db,
                allergen_name=allergen_name,
            )

            # Connect allergen to ingredient
            ingredient.allergens.append(allergen)

        # Save ingredient
        db.add(ingredient)
        db.commit()
        db.refresh(ingredient)

        return ingredient
    
    except VendorNotFoundError:
        db.rollback()
        raise
    
    except SQLAlchemyError:
        db.rollback()
        raise