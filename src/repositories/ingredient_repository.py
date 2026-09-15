"""Repository functions for ingredient database operations."""

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from constants.entity_types import EntityType
from deactivation_log.deactivation_log_schema import DeactivationLogSchema
from exceptions.ingredient_exceptions import (
    IngredientAlreadyInactiveError,
    IngredientAlreadyExistsError,
    IngredientConstraintError,
    IngredientNotFoundError,
    VendorNotFoundError,
)
from ingredient.ingredient_model import Ingredient
from ingredient.ingredient_schema import AllergenSchema, IngredientSchema
from repositories.deactivate_audit_repository import AuditRepository
from repositories.deactivation_log_repository import DeactivationLogRepository
from vendor.vendor_schema import Vendor


def get_or_create_allergen(
    db: Session,
    allergen_name: str,
) -> AllergenSchema:
    """Return an existing allergen or create a new one."""
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


class IngredientRepository:
    """Repository for managing ingredient-related database operations."""

    def __init__(
        self,
        db: Session,
        audit_db: Session | None = None,
    ):
        """Initialize the ingredient repository."""
        self.db = db
        self.audit_db = audit_db

    def create_ingredient(
        self,
        ingredient_data: Ingredient,
    ) -> IngredientSchema:
        """Create an ingredient and associate its allergens."""
        try:
            vendor = (
                self.db.query(Vendor)
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

            self.db.add(ingredient)

            for allergen_name in unique_allergens:
                allergen = get_or_create_allergen(
                    db=self.db,
                    allergen_name=allergen_name,
                )
                ingredient.allergens.append(allergen)

            self.db.commit()
            self.db.refresh(ingredient)

            return ingredient

        except VendorNotFoundError:
            self.db.rollback()
            raise

        except IntegrityError as exc:
            self.db.rollback()

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
            self.db.rollback()
            raise exc

    def get_all_ingredients(self) -> list[IngredientSchema]:
        """Return all ingredients."""
        return self.db.query(IngredientSchema).all()

    def get_deactivated_ingredients(
        self,
    ) -> list[IngredientSchema]:
        """Return all ingredients that have been deactivated."""
        return (
            self.db.query(IngredientSchema)
            .filter(IngredientSchema.active.is_(False))
            .all()
        )

    def get_ingredient_by_id(
        self,
        ingredient_id: int,
    ) -> IngredientSchema | None:
        """Retrieve an ingredient by its ID."""
        return (
            self.db.query(IngredientSchema)
            .filter(IngredientSchema.id == ingredient_id)
            .first()
        )

    def update_ingredient(
        self,
        ingredient_id: int,
        ingredient_data: Ingredient,
    ) -> IngredientSchema | None:
        """Update an existing ingredient."""
        try:
            ingredient = (
                self.db.query(IngredientSchema)
                .filter(IngredientSchema.id == ingredient_id)
                .first()
            )

            if ingredient is None:
                raise IngredientNotFoundError(ingredient_id)

            vendor = (
                self.db.query(Vendor)
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
                    db=self.db,
                    allergen_name=allergen_name,
                )
                ingredient.allergens.append(allergen)

            self.db.commit()
            self.db.refresh(ingredient)

            return ingredient

        except VendorNotFoundError:
            self.db.rollback()
            raise

        except IngredientNotFoundError:
            self.db.rollback()
            raise

        except IntegrityError as exc:
            self.db.rollback()

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
            self.db.rollback()
            raise exc

    def soft_delete_ingredient(
        self,
        ingredient_id: int,
        employee_id: int,
    ) -> IngredientSchema | None:
        """
        Deactivate an ingredient and record the deactivation event.

        The ingredient is soft deleted by setting active to False.
        Existing active recipe relationships are recorded using the
        existing deactivation log repository.

        The audit record is written using the existing audit repository,
        which automatically records the deactivation timestamp and the
        user performing the action.
        """
        try:
            ingredient = self.get_ingredient_by_id(ingredient_id)

            if ingredient is None:
                return None

            if not ingredient.active:
                raise IngredientAlreadyInactiveError(
                    ingredient_id
                )

            active_recipes = [
                recipe_link.drink_recipe
                for recipe_link in ingredient.ingredient_recipes
                if recipe_link.drink_recipe is not None
                and recipe_link.drink_recipe.active
            ]

            ingredient.active = False

            log_repo = DeactivationLogRepository(self.db)

            for recipe in active_recipes:
                log_repo.create(
                    entity_type="Ingredient",
                    entity_id=ingredient.id,
                    entity_name=ingredient.name,
                    related_entity_type="DrinkRecipe",
                    related_entity_id=recipe.id,
                    related_entity_name=recipe.name,
                    reason="Active relationship",
                    error_message=(
                        f"Ingredient {ingredient.name} was deactivated "
                        f"while still referenced by active drink recipe "
                        f"{recipe.name}."
                    ),
                )

            self.db.commit()
            self.db.refresh(ingredient)

            # Write the audit record after the ingredient has been
            # successfully deactivated.
            if self.audit_db is not None:
                audit_repo = AuditRepository(self.audit_db)

                audit_repo.record_deactivation(
                    item_id=ingredient.id,
                    item_name=ingredient.name,
                    user=str(employee_id),
                    item_type=EntityType.INGREDIENT,
                )

            return ingredient

        except IngredientAlreadyInactiveError:
            self.db.rollback()
            raise

        except SQLAlchemyError as exc:
            self.db.rollback()
            raise exc

    def get_ingredient_deactivation_history(
        self,
        ingredient_id: int,
        audit_db: Session,
    ) -> list[DeactivationLogSchema]:
        """
        Return audit records for a specific ingredient.

        This method queries the audit table directly rather than changing
        the shared AuditRepository.
        """
        from deactivation_log.deactivation_schema import DeactivationRecord

        return (
            audit_db.query(DeactivationRecord)
            .filter(
                DeactivationRecord.item_id == ingredient_id,
                DeactivationRecord.entity_type_id
                == EntityType.INGREDIENT.value,
            )
            .order_by(
                DeactivationRecord.deactivated_at.desc(),
                DeactivationRecord.id.desc(),
            )
            .all()
        )
