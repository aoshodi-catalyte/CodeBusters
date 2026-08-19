import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base
from vendor.vendor_router import router, get_db
from ingredient.ingredient_schema import IngredientSchema, AllergenSchema
from baked_good.baked_good_schema import BakedGoodSchema


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    test_app = FastAPI()
    test_app.include_router(router)
    test_app.dependency_overrides[get_db] = override_get_db

    with TestClient(test_app) as test_client:
        yield test_client

    Base.metadata.drop_all(bind=engine)


def test_post_new_vendor(client):
    vendor_payload = {
        "active": True,
        "name": "Bob's Burgers",
        "contact_name": "Bob Belcher",
        "contact_role": "CEO",
        "email": "bestburgers@burger.com",
        "phone": "1234567896",
    }

    response = client.post("/vendors", json=vendor_payload)

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Bob's Burgers"
    assert data["contact_name"] == "Bob Belcher"
    assert data["contact_role"] == "CEO"
    assert data["email"] == "bestburgers@burger.com"
    assert data["phone"] == "123-456-7896"
