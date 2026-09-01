from fastapi import status
import pytest

import ingredient
from tests.factories.drink_recipe_factories import (
    drink_types,
    ingredient_factory,
    recipe_payload_factory,
)


def test_create_drink_recipe(client, db, drink_types, ingredient_factory, recipe_payload_factory):
    ing1 = ingredient_factory("Sugar", 5.50, 10.00, "lb")
    ing2 = ingredient_factory("Milk", 7.30, 1.00, "gal")

    payload = recipe_payload_factory(
        name="Sweet Coffee",
        description="Coffee with sugar and milk",
        ingredients=[
            (ing1, 5.00, "g"),
            (ing2, 16.00, "fl_oz"),
        ],
        drink_type="coffee",
        markup=100,
    )

    response = client.post("/drink_recipes/", json=payload)
    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()
    assert data["name"] == "Sweet Coffee"
    assert data["type"] == "coffee"
    assert len(data["ingredients"]) == 2

    sugar, milk = data["ingredients"]

    assert sugar["name"] == "Sugar"
    assert sugar["quantity_used"] == 5.00
    assert sugar["unit_of_measure_used"] == "g"

    assert milk["name"] == "Milk"
    assert milk["quantity_used"] == 16.00
    assert milk["unit_of_measure_used"] == "fl_oz"

    assert data["production_cost"] == 0.92
    assert data["sale_price"] == 1.84


def test_duplicate_drink_name_rejected(client, db, drink_types, recipe_payload_factory):
    payload = recipe_payload_factory(
        name="Sweet Coffee",
        description="Coffee with sugar",
        ingredients=[],
        drink_type="coffee",
        markup=20,
    )

    first = client.post("/drink_recipes/", json=payload)
    assert first.status_code == status.HTTP_201_CREATED

    second = client.post("/drink_recipes/", json=payload)
    assert second.status_code == status.HTTP_409_CONFLICT
    assert "already exists" in second.json()["detail"].lower()


def test_negative_quantity_used(client, db, drink_types, ingredient_factory, recipe_payload_factory):
    ing = ingredient_factory("Milk", 7.30, 1.00, "gal")

    payload = recipe_payload_factory(
        name="Negative Quantity Used",
        description="Should fail",
        ingredients=[(ing, -16.00, "oz")],
        drink_type="tea",
        markup=20,
    )

    response = client.post("/drink_recipes/", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert any(
        "greater than 0" in err["msg"].lower()
        for err in response.json()["detail"]
    )


def test_invalid_ingredient_id(client, db, drink_types, recipe_payload_factory):
    fake = type("Fake", (), {"id": 9999})

    payload = recipe_payload_factory(
        name="Invalid Ingredient Drink",
        description="Should fail",
        ingredients=[(fake, 10, "g")],
        drink_type="coffee",
        markup=20,
    )

    response = client.post("/drink_recipes/", json=payload)
    assert response.status_code == status.HTTP_409_CONFLICT
    assert "ingredient id" in response.json()["detail"].lower()


def test_get_drink_recipe_by_id(client, db, drink_types, ingredient_factory, recipe_payload_factory):
    ing1 = ingredient_factory("Sugar", 5.50, 10.00, "lb")
    ing2 = ingredient_factory("Green Tea", 7.30, 100.00, "g")

    payload = recipe_payload_factory(
        name="Plain Tea",
        description="Simple tea",
        ingredients=[
            (ing1, 5.00, "g"),
            (ing2, 10.00, "g"),
        ],
        drink_type="tea",
        markup=81,
    )

    created = client.post("/drink_recipes/", json=payload).json()
    recipe_id = created["id"]

    response = client.get(f"/drink_recipes/{recipe_id}")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["id"] == recipe_id
    assert data["name"] == "Plain Tea"
    assert len(data["ingredients"]) == 2


def test_get_drink_recipe_by_id_not_found(client):
    response = client.get("/drink_recipes/9999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.json()["detail"].lower()


def test_invalid_drink_type(client, db, drink_types, recipe_payload_factory):
    payload = recipe_payload_factory(
        name="A",
        description="desc",
        ingredients=[],
        drink_type="not valid",
        markup=10,
    )

    response = client.post("/drink_recipes/", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_all_valid_drink_types(client, db, drink_types, recipe_payload_factory):
    recipes = [
        recipe_payload_factory("A", "desc", [], "Coffee", 10),
        recipe_payload_factory("B", "desc", [], "tea", 15),
        recipe_payload_factory("C", "desc", [], "Soda", 20),
        recipe_payload_factory("D", "desc", [], "other", 25),
    ]

    for r in recipes:
        client.post("/drink_recipes/", json=r)

    response = client.get("/drink_recipes/")
    assert response.status_code == status.HTTP_200_OK

    names = [r["name"] for r in response.json()]
    assert names == ["A", "B", "C", "D"]


def test_get_all_drink_recipes(client, db, drink_types, ingredient_factory, recipe_payload_factory):
    ing1 = ingredient_factory("Sugar", 5.50, 10.00, "lb")
    ing2 = ingredient_factory("Green Tea", 7.30, 100.00, "g")

    r1 = recipe_payload_factory("A", "desc", [(ing1, 5.00, "g"), (ing2, 10.00, "g")], "tea", 10)
    r2 = recipe_payload_factory("B", "desc", [], "coffee", 15)

    client.post("/drink_recipes/", json=r1)
    client.post("/drink_recipes/", json=r2)

    response = client.get("/drink_recipes/")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "A"
    assert data[1]["name"] == "B"


def test_get_all_returns_empty_list(client, db):
    response = client.get("/drink_recipes/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_update_drink_recipe_success(client, db, drink_types, ingredient_factory, recipe_payload_factory):
    ing = ingredient_factory("Milk", 8.00, 1.00, "gal")

    payload = recipe_payload_factory(
        name="Latte",
        description="Steamed milk + espresso",
        ingredients=[(ing, 6.0, "fl_oz")],
        drink_type="coffee",
        markup=20,
    )

    # Create initial recipe
    response = client.post("/drink_recipes/", json=payload)
    recipe_id = response.json()["id"]

    # Update payload
    updated_payload = recipe_payload_factory(
        name="Updated Latte",
        description="New desc",
        ingredients=[(ing, 8.0, "fl_oz")],
        drink_type="coffee",
        markup=50,
    )

    update_response = client.put(
        f"/drink_recipes/{recipe_id}",
        json=updated_payload
    )

    assert update_response.status_code == status.HTTP_200_OK
    data = update_response.json()

    assert data["name"] == "Updated Latte"
    assert data["description"] == "New desc"
    assert data["markup_percentage"] == 50
    assert data["production_cost"] > 0
    assert data["sale_price"] > data["production_cost"]


def test_update_drink_recipe_replaces_ingredients(client, db, drink_types, ingredient_factory, recipe_payload_factory):
    milk = ingredient_factory("Milk", 8.00, 1.00, "gal")
    sugar = ingredient_factory("Sugar", 5.00, 1.00, "lb")
    espresso = ingredient_factory("Espresso", 14.00, 1.00, "lb")

    # Initial recipe: Milk + Sugar
    initial_payload = recipe_payload_factory(
        name="Latte",
        description="Milk and sugar",
        ingredients=[
            (milk, 6.0, "fl_oz"),
            (sugar, 5.0, "g"),
        ],
        drink_type="coffee",
        markup=20,
    )

    create_response = client.post(
        "/drink_recipes/",
        json=initial_payload,
    )
    assert create_response.status_code == status.HTTP_201_CREATED

    recipe_id = create_response.json()["id"]

    # Update recipe: Milk + Espresso
    # Sugar should be removed.
    updated_payload = recipe_payload_factory(
        name="Updated Latte",
        description="Milk and espresso",
        ingredients=[
            (milk, 8.0, "fl_oz"),
            (espresso, 4.0, "oz"),
        ],
        drink_type="coffee",
        markup=30,
    )

    update_response = client.put(
        f"/drink_recipes/{recipe_id}",
        json=updated_payload,
    )

    assert update_response.status_code == status.HTTP_200_OK

    data = update_response.json()

    assert data["name"] == "Updated Latte"
    assert data["description"] == "Milk and espresso"
    assert len(data["ingredients"]) == 2

    ingredient_names = {
        ingredient["name"]
        for ingredient in data["ingredients"]
    }

    assert ingredient_names == {"Milk", "Espresso"}
    assert "Sugar" not in ingredient_names

    # Verify the replacement persisted in the database.
    get_response = client.get(
        f"/drink_recipes/{recipe_id}",
    )

    assert get_response.status_code == status.HTTP_200_OK

    persisted = get_response.json()

    persisted_names = {
        ingredient["name"]
        for ingredient in persisted["ingredients"]
    }

    assert persisted_names == {"Milk", "Espresso"}


def test_update_drink_recipe_invalid_ingredient_rolls_back(client, db, drink_types, ingredient_factory, recipe_payload_factory):
    milk = ingredient_factory("Milk", 8.00, 1.00, "gal")
    sugar = ingredient_factory("Sugar", 5.00, 1.00, "lb")

    initial_payload = recipe_payload_factory(
        name="Latte",
        description="Original recipe",
        ingredients=[
            (milk, 6.0, "fl_oz"),
            (sugar, 5.0, "g"),
        ],
        drink_type="coffee",
        markup=20,
    )

    create_response = client.post(
        "/drink_recipes/",
        json=initial_payload,
    )
    assert create_response.status_code == status.HTTP_201_CREATED

    original = create_response.json()
    recipe_id = original["id"]

    # Attempt to replace ingredients with one that does not exist.
    bad_payload = recipe_payload_factory(
        name="Changed Latte",
        description="This update should fail",
        ingredients=[
            (milk, 10.0, "fl_oz"),
            (type("Fake", (), {"id": 999999}), 5.0, "g"),
        ],
        drink_type="coffee",
        markup=50,
    )

    update_response = client.put(
        f"/drink_recipes/{recipe_id}",
        json=bad_payload,
    )

    assert update_response.status_code == status.HTTP_409_CONFLICT

    # Verify the original recipe was not partially modified.
    get_response = client.get(
        f"/drink_recipes/{recipe_id}",
    )

    assert get_response.status_code == status.HTTP_200_OK

    persisted = get_response.json()

    assert persisted["name"] == "Latte"
    assert persisted["description"] == "Original recipe"
    assert persisted["markup_percentage"] == 20

    assert len(persisted["ingredients"]) == 2

    ingredients_by_name = {
        ingredient["name"]: ingredient
        for ingredient in persisted["ingredients"]
    }

    assert set(ingredients_by_name) == {"Milk", "Sugar"}

    assert ingredients_by_name["Milk"]["quantity_used"] == 6.0
    assert ingredients_by_name["Milk"]["unit_of_measure_used"] == "fl_oz"

    assert ingredients_by_name["Sugar"]["quantity_used"] == 5.0
    assert ingredients_by_name["Sugar"]["unit_of_measure_used"] == "g"

    # Pricing should also remain unchanged.
    assert persisted["production_cost"] == original["production_cost"]
    assert persisted["sale_price"] == original["sale_price"]


def test_update_drink_recipe_not_found(client, db, drink_types, ingredient_factory, recipe_payload_factory):
    ing = ingredient_factory()
    payload = recipe_payload_factory(
        name="Latte",
        description="desc",
        ingredients=[(ing, 10.0, "fl_oz")],
        drink_type="coffee",
        markup=20,
    )

    response = client.put("/drink_recipes/999", json=payload)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_drink_recipe_ingredient_not_found(client, db, drink_types, ingredient_factory, recipe_payload_factory):
    ing = ingredient_factory()

    payload = recipe_payload_factory(
        name="Latte",
        description="desc",
        ingredients=[(ing, 8.0, "fl_oz")],
        drink_type="coffee",
        markup=20,
    )

    # Create recipe
    response = client.post("/drink_recipes/", json=payload)
    recipe_id = response.json()["id"]

    # Update with invalid ingredient ID
    bad_payload = recipe_payload_factory(
        name="Latte",
        description="desc",
        ingredients=[(type("Fake", (), {"id": 999}), 1.0, "fl_oz")],
        drink_type="coffee",
        markup=20,
    )

    update_response = client.put(
        f"/drink_recipes/{recipe_id}",
        json=bad_payload
    )

    assert update_response.status_code == status.HTTP_409_CONFLICT


def test_update_drink_recipe_drink_type_not_found(client, db, drink_types, ingredient_factory, recipe_payload_factory):
    ing = ingredient_factory()

    payload = recipe_payload_factory(
        name="Latte",
        description="desc",
        ingredients=[(ing, 10.0, "fl_oz")],
        drink_type="coffee",
        markup=20,
    )

    # Create recipe
    response = client.post("/drink_recipes/", json=payload)
    recipe_id = response.json()["id"]

    # Remove drink types
    db.query(type(next(iter(drink_types.values())))).delete()
    db.commit()

    bad_payload = recipe_payload_factory(
        name="Latte",
        description="desc",
        ingredients=[(ing, 1.0, "fl_oz")],
        drink_type="coffee",
        markup=20,
    )

    update_response = client.put(
        f"/drink_recipes/{recipe_id}",
        json=bad_payload
    )

    assert update_response.status_code == status.HTTP_404_NOT_FOUND


def test_update_drink_recipe_duplicate_name(client, db, drink_types, ingredient_factory, recipe_payload_factory):
    ing = ingredient_factory()

    # Create first recipe
    payload1 = recipe_payload_factory(
        name="Latte",
        description="desc",
        ingredients=[(ing, 10.0, "fl_oz")],
        drink_type="coffee",
        markup=20,
    )
    r1 = client.post("/drink_recipes/", json=payload1)
    assert r1.status_code == 201, r1.json()

    # Create second recipe
    payload2 = recipe_payload_factory(
        name="Mocha",
        description="desc",
        ingredients=[(ing, 10.0, "fl_oz")],
        drink_type="coffee",
        markup=20,
    )
    r2 = client.post("/drink_recipes/", json=payload2)
    assert r2.status_code == 201, r2.json()
    r2_json = r2.json()

    # Try updating second recipe to use first recipe's name
    updated_payload2 = recipe_payload_factory(
        name="Latte",
        description="desc",
        ingredients=[(ing, 10.0, "fl_oz")],
        drink_type="coffee",
        markup=20,
    )

    response = client.put(
        f"/drink_recipes/{r2_json['id']}",
        json=updated_payload2
    )

    assert response.status_code == 409


def test_update_drink_recipe_negative_quantity_returns_422(client, db, drink_types, ingredient_factory, recipe_payload_factory):
    milk = ingredient_factory("Milk", 8.00, 1.00, "gal")

    initial_payload = recipe_payload_factory(
        name="Latte",
        description="Original recipe",
        ingredients=[
            (milk, 6.0, "fl_oz"),
        ],
        drink_type="coffee",
        markup=20,
    )

    create_response = client.post(
        "/drink_recipes/",
        json=initial_payload,
    )
    assert create_response.status_code == status.HTTP_201_CREATED

    recipe_id = create_response.json()["id"]

    invalid_payload = recipe_payload_factory(
        name="Updated Latte",
        description="Invalid quantity",
        ingredients=[
            (milk, -10.0, "fl_oz"),
        ],
        drink_type="coffee",
        markup=20,
    )

    response = client.put(
        f"/drink_recipes/{recipe_id}",
        json=invalid_payload,
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    assert any(
        "greater than 0" in error["msg"].lower()
        for error in response.json()["detail"]
    )


def test_deactivate_drink_recipe_success(client, db, drink_types, recipe_payload_factory):
    """DELETE /drink_recipes/{id} should deactivate the recipe and return 204."""
    recipe = recipe_payload_factory(
        name="Americano",
        description="desc",
        ingredients=[],
        active=True,
        markup=50
    )

    created = client.post(
        "/drink_recipes/",
        json=recipe,
    )
    assert created.status_code == status.HTTP_201_CREATED

    recipe_id = created.json()["id"]

    response = client.delete(f"/drink_recipes/{recipe_id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.text == ""  # DELETE 204 returns no body

    updated = client.get(f"/drink_recipes/{recipe_id}")
    assert updated.json()["active"] == False


def test_deactivate_drink_recipe_not_found(client):
    """DELETE should return 404 when recipe does not exist."""
    response = client.delete("/drink_recipes/999")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.json()["detail"].lower()


def test_deactivate_drink_recipe_already_inactive(client, db, drink_types, recipe_payload_factory):
    """DELETE should return 409 when recipe is already inactive."""
    recipe = recipe_payload_factory(
        name="Cappuccino",
        description="desc",
        ingredients=[],
        active=False,
        markup=50
    )
    
    created = client.post(
        "/drink_recipes/",
        json=recipe,
    )
    assert created.status_code == status.HTTP_201_CREATED

    recipe_id = created.json()["id"]

    response = client.delete(f"/drink_recipes/{recipe_id}")

    assert response.status_code == status.HTTP_409_CONFLICT
    assert "already" in response.json()["detail"].lower()
