import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from tokenvault import TokenVault
import tempfile
import os


# FastAPI app setup (same as in README example)
app = FastAPI()
security = HTTPBearer()
vault = TokenVault()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    user_data = vault.validate(token)
    
    if user_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_data

@app.get("/protected")
async def protected_route(user_data: dict = Depends(get_current_user)):
    return {"message": "Access granted", "user": user_data}

@app.get("/public")
async def public_route():
    return {"message": "This is a public endpoint"}


def test_public_endpoint():
    """Test that public endpoints work without authentication"""
    client = TestClient(app)
    response = client.get("/public")
    assert response.status_code == 200
    assert response.json() == {"message": "This is a public endpoint"}


def test_protected_endpoint_without_token():
    """Test that protected endpoints require authentication"""
    client = TestClient(app)
    response = client.get("/protected")
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}


def test_protected_endpoint_with_invalid_token():
    """Test that invalid tokens are rejected"""
    client = TestClient(app)
    response = client.get("/protected", headers={"Authorization": "Bearer invalid_token"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid authentication token"}


def test_protected_endpoint_with_valid_token():
    """Test that valid tokens work correctly"""
    # Add a user to the vault
    token = vault.add("test@example.com", {"name": "Test User", "role": "admin"})
    
    client = TestClient(app)
    response = client.get("/protected", headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Access granted"
    assert data["user"]["name"] == "Test User"
    assert data["user"]["role"] == "admin"


def test_protected_endpoint_with_removed_user():
    """Test that removed users can't access protected endpoints"""
    # Add a user and get their token
    token = vault.add("temp@example.com", {"name": "Temporary User"})
    
    # Verify the token works initially
    client = TestClient(app)
    response = client.get("/protected", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    
    # Remove the user
    vault.remove("temp@example.com")
    
    # Verify the token no longer works
    response = client.get("/protected", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid authentication token"}


def test_multiple_users():
    """Test that different users get their own data"""
    # Add multiple users
    token1 = vault.add("user1@example.com", {"name": "User One", "id": 1})
    token2 = vault.add("user2@example.com", {"name": "User Two", "id": 2})
    
    client = TestClient(app)
    
    # Test user 1
    response1 = client.get("/protected", headers={"Authorization": f"Bearer {token1}"})
    assert response1.status_code == 200
    user1_data = response1.json()["user"]
    assert user1_data["name"] == "User One"
    assert user1_data["id"] == 1
    
    # Test user 2
    response2 = client.get("/protected", headers={"Authorization": f"Bearer {token2}"})
    assert response2.status_code == 200
    user2_data = response2.json()["user"]
    assert user2_data["name"] == "User Two"
    assert user2_data["id"] == 2
    
    # Verify they're different
    assert user1_data != user2_data


def test_vault_persistence_with_fastapi():
    """Test that vault persistence works with FastAPI"""
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        vault_path = tmp_file.name
    
    try:
        # Create vault with data
        test_vault = TokenVault()
        token = test_vault.add("persistent@example.com", {"name": "Persistent User"})
        test_vault.save(vault_path)
        
        # Create new FastAPI app with persistent vault
        persistent_app = FastAPI()
        persistent_vault = TokenVault(vault_path)
        
        async def get_persistent_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
            token = credentials.credentials
            user_data = persistent_vault.validate(token)
            
            if user_data is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication token",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            return user_data
        
        @persistent_app.get("/protected")
        async def persistent_protected_route(user_data: dict = Depends(get_persistent_user)):
            return {"message": "Access granted", "user": user_data}
        
        # Test that the token works with the persistent vault
        client = TestClient(persistent_app)
        response = client.get("/protected", headers={"Authorization": f"Bearer {token}"})
        
        assert response.status_code == 200
        data = response.json()
        assert data["user"]["name"] == "Persistent User"
        
    finally:
        # Clean up
        if os.path.exists(vault_path):
            os.unlink(vault_path)
