from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200

def test_create_item():
    response = client.post(
        "/items/",
        params={"name": "Notebook", "price": 45000.0, "category": "Electronics", "stock": 5}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"