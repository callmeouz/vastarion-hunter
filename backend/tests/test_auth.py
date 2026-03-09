from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Vastarion Hunter API is running!"

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["api"] == "healthy"

def test_register():
    response = client.post("/auth/register", json={
        "email": "test@test.com",
        "username": "testuser",
        "password": "test123"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@test.com"
    assert data["username"] == "testuser"
    assert data["role"] == "user"

def test_register_duplicate():
    response = client.post("/auth/register", json={
        "email": "test@test.com",
        "username": "testuser2",
        "password": "test123"
    })
    assert response.status_code == 400

def test_login():
    response = client.post("/auth/login", data={
        "username": "test@test.com",
        "password": "test123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data

def test_login_wrong_password():
    response = client.post("/auth/login", data={
        "username": "test@test.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401