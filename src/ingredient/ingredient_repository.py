"""Repository functions for ingredient database operations."""

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from ingredient.ingredient_exceptions import (
    IngredientAlreadyExistsError,
    IngredientConstraintError,
    VendorNotFoundError,
)
from ingredient.ingredient_model import Ingredient
from ingredient.ingredient_schema import AllergenSchema, IngredientSchema
from vendor.vendor_schema import Vendor


def get_or_create_allergen(
    db: Session,
    allergen_name: str,
) -> AllergenSchema:
    """Return an existing allergen or create a new one.

    Args:
        db: Active SQLAlchemy database session.
        allergen_name: Name of the allergen.

    Returns:
        The existing or newly created allergen.
    """
    allergen = (
        db.query(AllergenSchema)
        .filter(AllergenSchema.name == allergen_name)
        .first()
    )

    if allergen is None:
        allergen = AllergenSchema(name=allergen_name)
        db.add(allergen)
        db.flush()

    return allergen


def create_ingredient(
    db: Session,
    ingredient_data: Ingredient,
) -> IngredientSchema:
    """Create an ingredient and associate its allergens.

    Args:
        db: Active SQLAlchemy database session.
        ingredient_data: Validated ingredient data.

    Returns:
        The newly created ingredient.

    Raises:
        VendorNotFoundError: If the specified vendor does not exist.
        IngredientAlreadyExistsError:
            If an ingredient with the same name already exists.
        IngredientConstraintError:
            If the ingredient violates a database constraint.
        SQLAlchemyError:
            If an unexpected database error occurs.
    """
    try:
        vendor = (
            db.query(Vendor)
            .filter(Vendor.id == ingredient_data.vendor_id)
            .first()
        )

        if vendor is None:
            raise VendorNotFoundError(ingredient_data.vendor_id)

        unique_allergens = list(
            dict.fromkeys(ingredient_data.allergens)
        )

        ingredient = IngredientSchema(
            active=ingredient_data.active,
            name=ingredient_data.name,
            purchasing_cost=ingredient_data.purchasing_cost,
            unit_amount=ingredient_data.unit_amount,
            unit_of_measure=ingredient_data.unit_of_measure,
            vendor_id=ingredient_data.vendor_id,
        )

        db.add(ingredient)

        for allergen_name in unique_allergens:
            allergen = get_or_create_allergen(
                db=db,
                allergen_name=allergen_name,
            )
            ingredient.allergens.append(allergen)

        db.commit()
        db.refresh(ingredient)

        return ingredient
    except VendorNotFoundError:
        db.rollback()
        raise

    except IntegrityError as exc:
        db.rollback()

        constraint = getattr(
            getattr(exc.orig, "diag", None),
            "constraint_name",
            None,
        )

        error_message = str(exc.orig).lower()

        if (
            constraint == "uq_ingredient_name"
            or "unique constraint failed: ingredient.name"
            in error_message
            or "uq_ingredient_name" in error_message
        ):
            raise IngredientAlreadyExistsError(
                ingredient_data.name
            ) from exc

        raise IngredientConstraintError(constraint) from exc

    except SQLAlchemyError as exc:
        db.rollback()
        raise exc


def get_all_ingredients(
    db: Session,
) -> list[IngredientSchema]:
    """Return all ingredients.

    Args:
        db: Active SQLAlchemy database session.

    Returns:
        A list containing all ingredients.
    """
    return db.query(IngredientSchema).all()


def get_ingredient_by_id(
    db: Session,
    ingredient_id: int,
) -> IngredientSchema | None:
    """Retrieve an ingredient by its ID.

    Args:
        db: Active SQLAlchemy database session.
        ingredient_id: ID of the ingredient to retrieve.

    Returns:
        The ingredient if it exists, otherwise None.
    """
    return (
        db.query(IngredientSchema)
        .filter(IngredientSchema.id == ingredient_id)
        .first()
    )


def update_ingredient(
    db: Session,
    ingredient_id: int,
    ingredient_data: Ingredient,
) -> IngredientSchema | None:
    """Update an existing ingredient.

    Args:
        db: Active SQLAlchemy database session.
        ingredient_id: ID of the ingredient to update.
        ingredient_data: Validated ingredient data.

    Returns:
        The updated ingredient, or None if it does not exist.

    Raises:
        VendorNotFoundError: If the specified vendor does not exist.
        IngredientAlreadyExistsError:
            If the updated name already belongs to another ingredient.
        IngredientConstraintError:
            If the update violates a database constraint.
        SQLAlchemyError:
            If an unexpected database error occurs.
    """
    try:
        ingredient = (
            db.query(IngredientSchema)
            .filter(IngredientSchema.id == ingredient_id)
            .first()
        )

        if ingredient is None:
            return None

        vendor = (
            db.query(Vendor)
            .filter(Vendor.id == ingredient_data.vendor_id)
            .first()
        )

        if vendor is None:
            raise VendorNotFoundError(ingredient_data.vendor_id)

        ingredient.active = ingredient_data.active
        ingredient.name = ingredient_data.name
        ingredient.purchasing_cost = ingredient_data.purchasing_cost
        ingredient.unit_amount = ingredient_data.unit_amount
        ingredient.unit_of_measure = ingredient_data.unit_of_measure
        ingredient.vendor_id = ingredient_data.vendor_id

        unique_allergens = list(
            dict.fromkeys(ingredient_data.allergens)
        )

        ingredient.allergens.clear()

        for allergen_name in unique_allergens:
            allergen = get_or_create_allergen(
                db=db,
                allergen_name=allergen_name,
            )
            ingredient.allergens.append(allergen)

        db.commit()
        db.refresh(ingredient)

        return ingredient

    except VendorNotFoundError:
        db.rollback()
        raise

    except IntegrityError as exc:
        db.rollback()

        constraint = getattr(
            getattr(exc.orig, "diag", None),
            "constraint_name",
            None,
        )

        error_message = str(exc.orig).lower()

        if (
            constraint == "uq_ingredient_name"
            or "unique constraint failed: ingredient.name"
            in error_message
            or "uq_ingredient_name" in error_message
        ):
            raise IngredientAlreadyExistsError(
                ingredient_data.name
            ) from exc

        raise IngredientConstraintError(constraint) from exc

    except SQLAlchemyError as exc:
        db.rollback()
        raise exc
