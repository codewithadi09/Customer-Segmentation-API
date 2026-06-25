import pytest
from fastapi.testclient import TestClient


# -------------------------
# SIGNUP TESTS
# -------------------------

def test_signup_success(client):
    """A new user can register successfully."""
    response = client.post("/signup", json={
        "username": "newuser",
        "password": "securepassword123"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "newuser"
    assert "id" in data
    assert "password" not in data  # password must never be returned


def test_signup_duplicate_username(client, registered_user):
    """Registering with an already-taken username returns 400."""
    response = client.post("/signup", json={
        "username": registered_user["username"],
        "password": "anotherpassword"
    })
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_signup_returns_no_password(client):
    """The signup response must never include a password field."""
    response = client.post("/signup", json={
        "username": "safeuser",
        "password": "mypassword"
    })
    data = response.json()
    assert "password" not in data
    assert "hashed_password" not in data


# -------------------------
# LOGIN TESTS
# -------------------------

def test_login_success(client, registered_user):
    """A registered user can log in and receive a JWT token."""
    response = client.post("/login", data={
        "username": registered_user["username"],
        "password": registered_user["password"]
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, registered_user):
    """Login with wrong password returns 401."""
    response = client.post("/login", data={
        "username": registered_user["username"],
        "password": "wrongpassword"
    })
    assert response.status_code == 401


def test_login_nonexistent_user(client):
    """Login with a username that doesn't exist returns 401."""
    response = client.post("/login", data={
        "username": "ghostuser",
        "password": "somepassword"
    })
    assert response.status_code == 401


# -------------------------
# PROTECTED ROUTE TESTS
# -------------------------

def test_me_with_valid_token(client, registered_user, auth_headers):
    """Authenticated user can access /me and get their profile."""
    response = client.get("/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["username"] == registered_user["username"]


def test_me_without_token(client):
    """Accessing /me without a token returns 401."""
    response = client.get("/me")
    assert response.status_code == 401


def test_me_with_invalid_token(client):
    """Accessing /me with a fake token returns 401."""
    response = client.get("/me", headers={
        "Authorization": "Bearer this.is.fake"
    })
    assert response.status_code == 401