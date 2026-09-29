import pytest
from app.models.user import User


def test_user_registration(client):
    payload = {
        "name": "Rohan Verma",
        "email": "rohan@example.com",
        "phone": "+91 99887 76655",
        "password": "mypassword123",
        "confirm_password": "mypassword123"
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "rohan@example.com"
    assert data["user"]["role"] == "USER"


def test_registration_password_mismatch(client):
    payload = {
        "name": "Mismatch User",
        "email": "mismatch@example.com",
        "password": "password123",
        "confirm_password": "different123"
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 400
    assert "match" in response.json()["detail"].lower()


def test_duplicate_email_registration(client, normal_user):
    payload = {
        "name": "Duplicate User",
        "email": normal_user.email,
        "password": "somepassword123",
        "confirm_password": "somepassword123"
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"].lower()


def test_login_success(client, normal_user):
    response = client.post("/api/auth/login", json={
        "email": normal_user.email,
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == normal_user.email


def test_login_invalid_credentials(client, normal_user):
    response = client.post("/api/auth/login", json={
        "email": normal_user.email,
        "password": "wrongpassword"
    })
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]


def test_get_current_user_profile(client, user_token):
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == "testuser@example.com"


def test_admin_route_forbidden_for_normal_user(client, user_token):
    # Attempting to fetch admin stats with normal user token
    response = client.get(
        "/api/admin/stats",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 403
    assert "administrative privileges required" in response.json()["detail"].lower()


def test_admin_route_allowed_for_admin_user(client, admin_token):
    response = client.get(
        "/api/admin/stats",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "total_users" in data
    assert "total_movies" in data
