"""
FastAPI test application for TokenVault authentication.
Run with: uvicorn tests.app:app --reload
Then visit: http://localhost:8000/docs
"""

import os
import tempfile
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from tokenvault import TokenVault

# Create a temporary vault for testing
vault_file = os.path.join(tempfile.gettempdir(), "test_vault.db")
vault = TokenVault()  # Start with empty vault

app = FastAPI(
    title="TokenVault API",
    description="Simple authentication API using TokenVault tokens",
    version="1.0.0"
)

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Authenticate user using TokenVault token"""
    token = credentials.credentials
    user_data = vault.validate(token)
    
    if user_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_data

@app.get("/")
async def root():
    """API information"""
    return {
        "message": "TokenVault API",
        "docs": "/docs",
        "endpoints": {
            "add": "POST /add - Add user and get token",
            "public": "GET /public - Public endpoint (no auth required)",
            "protected": "GET /protected - Protected endpoint (requires token)"
        },
        "curl_examples": {
            "add_user": 'curl -X POST "http://localhost:8001/add" -H "Content-Type: application/json" -d \'{"email": "user@example.com"}\'',
            "public": 'curl http://localhost:8001/public',
            "protected": 'curl -H "Authorization: Bearer <token>" http://localhost:8001/protected'
        }
    }

@app.post("/add")
async def add_user(email: str):
    """Add a new user and get their token"""
    try:
        token = vault.add(email, {"email": email, "created_at": datetime.now().isoformat()})
        
        # Create a copy-paste ready curl command with proper quoting
        curl_command = f"curl -H 'Authorization: Bearer {token}' http://localhost:8001/protected"
        
        return {
            "success": True,
            "message": f"User {email} added successfully",
            "token": token,
            "user_data": {
                "email": email,
            },
            "copy_paste_curl": curl_command,
            "instructions": {
                "step1": "Copy the token above",
                "step2": "Copy and paste this curl command:",
                "step3": "Or use the token in Swagger UI 'Authorize' button"
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to add user: {str(e)}"
        )

@app.get("/public")
async def public_endpoint():
    """Public endpoint - no authentication required"""
    return {
        "message": "This is a public endpoint",
        "status": "accessible to everyone",
        "timestamp": datetime.now().isoformat(),
        "curl_example": "curl http://localhost:8001/public"
    }

@app.get("/protected")
async def protected_endpoint(user_data: dict = Depends(get_current_user)):
    """Protected endpoint - requires valid token"""
    return {
        "message": "Access granted to protected resource",
        "user": user_data,
        "status": "authenticated",
        "timestamp": datetime.now().isoformat(),
        "curl_example": 'curl -H "Authorization: Bearer <token>" http://localhost:8001/protected'
    }

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("TokenVault API")
    print("="*60)
    print("Endpoints:")
    print("- POST /add - Add user and get token")
    print("- GET /public - Public endpoint (no auth required)")
    print("- GET /protected - Protected endpoint (requires token)")
    print("="*60)
    print("Start server: uvicorn tests.app:app --reload")
    print("Visit: http://localhost:8001/docs")
    print("="*60)
