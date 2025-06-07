import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_user():
    payload = {"email": "testuser@example.com", "name": "Test User"}
    response = client.post("/users/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == payload["email"]
    assert data["name"] == payload["name"]
    assert "id" in data
    assert "created_at" in data


def test_get_user_by_id():
    payload = {"email": "getbyid@example.com", "name": "Get By ID"}
    create_resp = client.post("/users/", json=payload)
    assert create_resp.status_code == 201
    user_id = create_resp.json()["id"]

    response = client.get(f"/users?id={user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id
    assert data["email"] == payload["email"]
    assert data["name"] == payload["name"]
    assert "created_at" in data


def test_list_users():
    payload = {"email": "listuser@example.com", "name": "List User"}
    client.post("/users/", json=payload)

    response = client.get("/users/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(user["email"] == payload["email"] for user in data)
