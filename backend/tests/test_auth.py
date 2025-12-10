import pytest
from jose import jwt
from app.core.config import settings

@pytest.mark.asyncio
async def test_health_check(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@pytest.mark.asyncio
async def test_register_success(client):
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "user@example.com", "password": "securepassword123"}
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_register_duplicate_email(client):
    # Register once
    await client.post(
        "/api/v1/auth/register",
        json={"email": "duplicate@example.com", "password": "pass123"}
    )
    # Register again
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "duplicate@example.com", "password": "pass123"}
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]

@pytest.mark.asyncio
async def test_login_success(client):
    # Register first
    await client.post(
        "/api/v1/auth/register",
        json={"email": "login@example.com", "password": "mypassword"}
    )
    # Login
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "login@example.com", "password": "mypassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data

@pytest.mark.asyncio
async def test_login_invalid_credentials(client):
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "notfound@example.com", "password": "wrong"}
    )
    assert response.status_code == 400
    assert "Incorrect email or password" in response.json()["detail"]

@pytest.mark.asyncio
async def test_refresh_token_success(client):
    # Register and login
    await client.post(
        "/api/v1/auth/register",
        json={"email": "refresh@example.com", "password": "pass"}
    )
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "refresh@example.com", "password": "pass"}
    )
    refresh_token = login_resp.json()["refresh_token"]

    # Refresh
    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    # Verify the tokens are valid JWT tokens
    assert len(data["access_token"].split(".")) == 3
    assert len(data["refresh_token"].split(".")) == 3

@pytest.mark.asyncio
async def test_refresh_token_invalid(client):
    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "invalid.token.here"}
    )
    assert response.status_code == 401
    assert "Invalid refresh token" in response.json()["detail"]

@pytest.mark.asyncio
async def test_access_token_decoding(client):
    # Register and login
    await client.post(
        "/api/v1/auth/register",
        json={"email": "decode@example.com", "password": "pass"}
    )
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "decode@example.com", "password": "pass"}
    )
    access_token = login_resp.json()["access_token"]

    # Decode token
    payload = jwt.decode(
        access_token,
        settings.secret_key,
        algorithms=[settings.algorithm]
    )
    assert payload["type"] == "access"
    assert "exp" in payload