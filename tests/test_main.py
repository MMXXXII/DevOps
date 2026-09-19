from fastapi.testclient import TestClient

from app.main import app
from uuid import uuid4

client = TestClient(app)


def test_read_main():
    response = client.get("/")

    assert response.status_code == 200


def test_create_item():
    response = client.post(
        "/items/",
        params={
            "name": "Notebook",
            "price": 45000.0,
            "category": "Electronics",
            "stock": 5
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "success"
    assert "id" in data


def test_get_items():
    response = client.get("/items/")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_item():
    create_response = client.post(
        "/items/",
        params={
            "name": "Mouse",
            "price": 2500.0,
            "category": "Electronics",
            "stock": 10
        }
    )

    item_id = create_response.json()["id"]

    response = client.get(f"/items/{item_id}")

    assert response.status_code == 200
    assert response.json()["name"] == "Mouse"


def test_update_item():
    create_response = client.post(
        "/items/",
        params={
            "name": "Old Name",
            "price": 1000.0,
            "category": "Test",
            "stock": 1
        }
    )

    item_id = create_response.json()["id"]

    response = client.put(
        f"/items/{item_id}",
        params={
            "name": "New Name",
            "price": 2000.0,
            "category": "Updated",
            "stock": 10
        }
    )

    assert response.status_code == 200
    assert response.json()["status"] == "updated"


def test_delete_item():
    create_response = client.post(
        "/items/",
        params={
            "name": "Delete Me",
            "price": 100.0,
            "category": "Test",
            "stock": 1
        }
    )

    item_id = create_response.json()["id"]

    response = client.delete(f"/items/{item_id}")

    assert response.status_code == 200
    assert response.json()["status"] == "deleted"


def test_search_by_name():
    response = client.get(
        "/items/search/name",
        params={"name": "Notebook"}
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_filter_by_price():
    response = client.get(
        "/items/filter/price",
        params={"max_price": 50000}
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_category():
    category_name = f"TestCategory-{uuid4().hex}"

    response = client.post(
        "/categories/",
        params={
            "name": category_name,
            "description": "Test category"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "success"
    assert "id" in data




def test_update_stock():
    create_response = client.post(
        "/items/",
        params={
            "name": "Keyboard",
            "price": 5000.0,
            "category": "Electronics",
            "stock": 3
        }
    )

    item_id = create_response.json()["id"]

    response = client.patch(
        f"/items/{item_id}/stock",
        params={"stock": 20}
    )

    assert response.status_code == 200
    assert response.json()["stock"] == 20

