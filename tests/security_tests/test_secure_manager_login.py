"""
Tests verifying that managers can perform write operations (POST, PUT, DELETE)
while employees are restricted to read-only GET operations.
"""

from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient

from security.secure_manager_login import check_role
from tests.factories.auth_factories import manager_token, employee_token


app = FastAPI()


@app.post("/items", dependencies=[Depends(check_role(["manager"]))])
def create_item():
    return {"message": "Item created"}


@app.put("/items/{item_id}", dependencies=[Depends(check_role(["manager"]))])
def update_item(item_id: int):
    return {"message": f"Item {item_id} updated"}


@app.delete("/items/{item_id}", dependencies=[Depends(check_role(["manager"]))])
def delete_item(item_id: int):
    return {"message": f"Item {item_id} deleted"}


@app.get("/items", dependencies=[Depends(check_role(["employee", "manager"]))])
def list_items():
    return [{"id": 1, "name": "Test Item"}]


client = TestClient(app)


def test_manager_can_post():
    token = manager_token()
    resp = client.post("/items", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["message"] == "Item created"


def test_manager_can_put():
    token = manager_token()
    resp = client.put("/items/1", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["message"] == "Item 1 updated"


def test_manager_can_delete():
    token = manager_token()
    resp = client.delete(
        "/items/1", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["message"] == "Item 1 deleted"


def test_manager_can_get():
    token = manager_token()
    resp = client.get("/items", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_employee_cannot_post():
    token = employee_token()
    resp = client.post("/items", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 403
    assert resp.json()[
        "detail"] == "You do not have permission to perform this action."


def test_employee_cannot_put():
    token = employee_token()
    resp = client.put("/items/1", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 403
    assert resp.json()[
        "detail"] == "You do not have permission to perform this action."


def test_employee_cannot_delete():
    token = employee_token()
    resp = client.delete(
        "/items/1", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 403
    assert resp.json()[
        "detail"] == "You do not have permission to perform this action."


def test_employee_can_get():
    token = employee_token()
    resp = client.get("/items", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
