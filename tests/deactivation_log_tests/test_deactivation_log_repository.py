from datetime import datetime

from deactivation_log.deactivation_log_schema import DeactivationLogSchema
from drink_recipe.drink_ingredients_schema import DrinkRecipeIngredientSchema
from drink_recipe.drink_recipe_schema import DrinkRecipeSchema
from drink_recipe.drink_type_schema import DrinkTypeSchema
from repositories.deactivation_log_repository import DeactivationLogRepository
from deactivation_log.deactivation_log_schema import DeactivationLogSchema
from repositories.ingredient_repository import IngredientRepository
from tests.ingredient_tests.test_ingredient_repository import make_ingredient
from vendor.vendor_schema import Vendor

def test_create_deactivation_log(db):
    repo = DeactivationLogRepository(db)

    log = repo.create(
        entity_type="Ingredient",
        entity_id=1,
        entity_name="Espresso",
        related_entity_type="DrinkRecipe",
        related_entity_id=10,
        related_entity_name="Iced Latte",
        reason="Active relationship during deactivation",
        error_message=(
            'Ingredient "Espresso" was deactivated while still '
            'referenced by active drink recipe "Iced Latte".'
        ),
    )

    db.commit()
    db.refresh(log)

    assert log.id is not None
    assert log.entity_type == "Ingredient"
    assert log.entity_id == 1
    assert log.entity_name == "Espresso"
    assert log.related_entity_type == "DrinkRecipe"
    assert log.related_entity_id == 10
    assert log.related_entity_name == "Iced Latte"
    assert log.reason == "Active relationship during deactivation"
    assert "Espresso" in log.error_message
    assert "Iced Latte" in log.error_message
    assert log.deactivated_at is not None


def test_get_all_deactivation_logs(db):
    repo = DeactivationLogRepository(db)

    repo.create(
        entity_type="Ingredient",
        entity_id=1,
        entity_name="Espresso",
        related_entity_type="DrinkRecipe",
        related_entity_id=10,
        related_entity_name="Iced Latte",
        reason="Active relationship during deactivation",
        error_message="Espresso is still used by Iced Latte.",
    )

    repo.create(
        entity_type="Ingredient",
        entity_id=2,
        entity_name="Milk",
        related_entity_type="DrinkRecipe",
        related_entity_id=11,
        related_entity_name="Cappuccino",
        reason="Active relationship during deactivation",
        error_message="Milk is still used by Cappuccino.",
    )

    db.commit()

    logs = repo.get_all()

    assert len(logs) == 2


def test_get_all_logs_newest_first(db):
    repo = DeactivationLogRepository(db)

    first = repo.create(
        entity_type="Ingredient",
        entity_id=1,
        entity_name="Espresso",
        related_entity_type="DrinkRecipe",
        related_entity_id=10,
        related_entity_name="Iced Latte",
        reason="Relationship found",
        error_message="Espresso is still used by Iced Latte.",
    )

    second = repo.create(
        entity_type="Ingredient",
        entity_id=2,
        entity_name="Milk",
        related_entity_type="DrinkRecipe",
        related_entity_id=11,
        related_entity_name="Cappuccino",
        reason="Relationship found",
        error_message="Milk is still used by Cappuccino.",
    )

    db.commit()

    # Make the ordering deterministic for this test.
    first.deactivated_at = datetime(2024, 1, 1)
    second.deactivated_at = datetime(2024, 1, 2)
    db.commit()

    logs = repo.get_all()

    assert logs[0].id == second.id
    assert logs[1].id == first.id


def test_get_all_logs_pagination(db):
    repo = DeactivationLogRepository(db)

    for number in range(1, 6):
        repo.create(
            entity_type="Ingredient",
            entity_id=number,
            entity_name=f"Ingredient {number}",
            related_entity_type="DrinkRecipe",
            related_entity_id=number,
            related_entity_name=f"Recipe {number}",
            reason="Relationship found",
            error_message=f"Ingredient {number} is still in use.",
        )

    db.commit()

    logs = (
        db.query(DeactivationLogSchema)
        .order_by(DeactivationLogSchema.id.asc())
        .offset(2)
        .limit(2)
        .all()
    )

    assert len(logs) == 2
    assert logs[0].entity_id == 3
    assert logs[1].entity_id == 4


def test_get_deactivation_log_by_id(db):
    repo = DeactivationLogRepository(db)

    log = repo.create(
        entity_type="Ingredient",
        entity_id=1,
        entity_name="Espresso",
        related_entity_type="DrinkRecipe",
        related_entity_id=10,
        related_entity_name="Iced Latte",
        reason="Relationship found",
        error_message="Espresso is still used by Iced Latte.",
    )

    db.commit()
    db.refresh(log)

    result = repo.get_by_id(log.id)

    assert result is not None
    assert result.id == log.id
    assert result.entity_name == "Espresso"


def test_get_missing_deactivation_log_returns_none(db):
    repo = DeactivationLogRepository(db)

    result = repo.get_by_id(999999)

    assert result is None

def test_soft_delete_ingredient_creates_deactivation_log(
    db,
):
    """Test that deleting an ingredient creates a deactivation log."""
    vendor = Vendor(
        name="Deactivation Log Vendor",
        contact_name="John Doe",
        contact_role="Sales",
        email="deactivationlog@test.com",
        phone="3125557000",
        active=True,
    )

    db.add(vendor)
    db.commit()
    db.refresh(vendor)

    # Create the ingredient.
    ingredient_repo = IngredientRepository(db)

    ingredient = ingredient_repo.create_ingredient(
        make_ingredient(
            name="Espresso",
            vendor_id=vendor.id,
        ),
    )

    # Create a drink type.
    drink_type = DrinkTypeSchema(
        name="coffee",
    )

    db.add(drink_type)
    db.commit()
    db.refresh(drink_type)

    # Create an active drink recipe.
    recipe = DrinkRecipeSchema(
        name="Iced Latte",
        description="Espresso with milk over ice",
        type_id=drink_type.id,
        active=True,
    )

    db.add(recipe)
    db.commit()
    db.refresh(recipe)

    # Connect the ingredient to the recipe.
    recipe_ingredient = DrinkRecipeIngredientSchema(
        drink_recipe_id=recipe.id,
        ingredient_id=ingredient.id,
        quantity_used=1.0,
        unit_of_measure_used="oz",
    )

    db.add(recipe_ingredient)
    db.commit()
    db.refresh(recipe_ingredient)

    # Deactivate the ingredient.
    result = ingredient_repo.soft_delete_ingredient(
        ingredient_id=ingredient.id,
    )

    # Verify the ingredient was deactivated.
    assert result is not None
    assert result.id == ingredient.id
    assert result.active is False

    # Verify a deactivation log was created.
    log = (
        db.query(DeactivationLogSchema)
        .filter(
            DeactivationLogSchema.entity_id == ingredient.id,
            DeactivationLogSchema.related_entity_id == recipe.id,
        )
        .first()
    )

    assert log is not None

    assert log.entity_type == "Ingredient"
    assert log.entity_id == ingredient.id
    assert log.entity_name == "Espresso"

    assert log.related_entity_type == "DrinkRecipe"
    assert log.related_entity_id == recipe.id
    assert log.related_entity_name == "Iced Latte"

    assert log.reason == "Active relationship"

    assert "Espresso" in log.error_message
    assert "Iced Latte" in log.error_message
