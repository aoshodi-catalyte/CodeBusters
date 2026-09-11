from deactivation_log.deactivation_log_schema import DeactivationLogSchema


def create_log(db, entity_id, entity_name, recipe_id, recipe_name):
    log = DeactivationLogSchema(
        entity_type="Ingredient",
        entity_id=entity_id,
        entity_name=entity_name,
        related_entity_type="DrinkRecipe",
        related_entity_id=recipe_id,
        related_entity_name=recipe_name,
        reason="Active relationship during deactivation",
        error_message=(
            f'Ingredient "{entity_name}" was deactivated while still '
            f'referenced by active drink recipe "{recipe_name}".'
        ),
    )

    db.add(log)
    db.commit()
    db.refresh(log)

    return log


def test_get_deactivation_logs_empty(client):
    response = client.get("/deactivation-logs/")

    assert response.status_code == 200
    assert response.json() == []


def test_get_deactivation_logs(client, db):
    create_log(
        db,
        entity_id=1,
        entity_name="Espresso",
        recipe_id=10,
        recipe_name="Iced Latte",
    )

    response = client.get("/deactivation-logs/")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["entity_type"] == "Ingredient"
    assert data[0]["entity_id"] == 1
    assert data[0]["entity_name"] == "Espresso"
    assert data[0]["related_entity_type"] == "DrinkRecipe"
    assert data[0]["related_entity_id"] == 10
    assert data[0]["related_entity_name"] == "Iced Latte"
    assert data[0]["reason"] == "Active relationship during deactivation"


def test_get_deactivation_log_by_id(client, db):
    log = create_log(
        db,
        entity_id=1,
        entity_name="Espresso",
        recipe_id=10,
        recipe_name="Iced Latte",
    )

    response = client.get(f"/deactivation-logs/{log.id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == log.id
    assert data["entity_name"] == "Espresso"
    assert data["related_entity_name"] == "Iced Latte"


def test_get_missing_deactivation_log_returns_404(client):
    response = client.get("/deactivation-logs/999999")

    assert response.status_code == 404

    data = response.json()

    assert data["detail"]["error"] == "deactivation_log_not_found"


def test_get_deactivation_logs_pagination(client, db):
    for number in range(1, 6):
        create_log(
            db,
            entity_id=number,
            entity_name=f"Ingredient {number}",
            recipe_id=number,
            recipe_name=f"Recipe {number}",
        )

    response = client.get(
        "/deactivation-logs/?skip=1&limit=2"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2


def test_get_deactivation_logs_rejects_zero_limit(client):
    response = client.get(
        "/deactivation-logs/?limit=0"
    )

    assert response.status_code == 422


def test_get_deactivation_logs_rejects_limit_over_100(client):
    response = client.get(
        "/deactivation-logs/?limit=101"
    )

    assert response.status_code == 422


def test_get_deactivation_logs_rejects_negative_skip(client):
    response = client.get(
        "/deactivation-logs/?skip=-1"
    )

    assert response.status_code == 422
