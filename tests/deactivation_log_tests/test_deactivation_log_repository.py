from datetime import datetime

from deactivation_log.deactivation_log_schema import DeactivationLogSchema
from repositories.deactivation_log_repository import DeactivationLogRepository
from deactivation_log.deactivation_log_schema import DeactivationLogSchema
from repositories.drink_recipe_repository import DrinkRecipeRepository
from repositories.ingredient_repository import IngredientRepository, soft_delete_ingredient

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
    drink_types,
    ingredient_factory,
    recipe_model_factory,
):
    """Deactivating an ingredient creates a log for active related recipes."""
    ingredient_repo = IngredientRepository(db)
    drink_repo = DrinkRecipeRepository(db)

    # Create the ingredient.
    ingredient = ingredient_factory(
        name="Espresso",
        cost=14.00,
        amount=1.00,
        uom="lb",
    )

    # Create an active recipe that uses the ingredient.
    recipe = recipe_model_factory(
        name="Espresso Latte",
        description="Espresso with milk",
        ingredients=[
            (ingredient, 2.00, "oz"),
        ],
        drink_type="coffee",
        markup=50,
        active=True,
    )

    created_recipe = drink_repo.create_drink_recipe(recipe)

    # Deactivate the ingredient.
    result = ingredient_repo.soft_delete_ingredient(
        ingredient_id=ingredient.id,
    )

    # Ingredient should now be inactive.
    assert result is not None
    assert result.id == ingredient.id
    assert result.active is False

    # A deactivation log should have been created.
    log = (
        db.query(DeactivationLogSchema)
        .filter(
            DeactivationLogSchema.entity_id == ingredient.id,
            DeactivationLogSchema.related_entity_id == created_recipe.id,
        )
        .first()
    )

    assert log is not None

    # Verify the log contains the expected information.
    assert log.entity_type == "Ingredient"
    assert log.entity_id == ingredient.id
    assert log.entity_name == "Espresso"

    assert log.related_entity_type == "DrinkRecipe"
    assert log.related_entity_id == created_recipe.id
    assert log.related_entity_name == "Espresso Latte"

    assert log.reason == "Deactivated while still referenced by an active drink recipe"
    assert "Espresso" in log.error_message
    assert "Espresso Latte" in log.error_message
