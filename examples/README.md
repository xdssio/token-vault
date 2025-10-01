# TokenVault Test App

A FastAPI test application to demonstrate TokenVault authentication.

## Quick Start

1. **Start the server:**
   ```bash   
   uvicorn examples.fastapi_example:app --port=8001 --reload
   ```

2. **Visit the API docs:**
   - Open: http://localhost:8001/docs
   - Interactive Swagger UI for testing endpoints

## Available Endpoints

### Public Endpoints (No Authentication Required)

- **GET /** - API information and available endpoints
- **GET /public** - Public endpoint accessible to everyone
- **POST /add** - Add a new user and get their token
- **POST /login** - Login with a token

### Protected Endpoints (Authentication Required)

- **GET /test** - Test authentication and get timestamp
- **POST /logout** - Logout (requires valid token)
- **GET /protected** - Protected resource access
- **GET /admin** - Admin-only endpoint (requires admin role)
- **GET /user-info** - Get detailed user information

## Testing Authentication

1. **Add a user:**
   ```bash
   curl -X POST "http://localhost:8000/add" \
        -H "Content-Type: application/json" \
        -d '{"email": "test@example.com", "name": "Test User", "role": "user"}'
   ```

2. **Login with token:**
   ```bash
   curl -X POST "http://localhost:8000/login" \
        -H "Content-Type: application/json" \
        -d '{"token": "YOUR_TOKEN_HERE"}'
   ```

3. **Test authenticated endpoint:**
   ```bash
   curl -X GET "http://localhost:8000/test" \
        -H "Authorization: Bearer YOUR_TOKEN_HERE"
   ```

## Using the Swagger UI

1. Go to http://localhost:8000/docs
2. Click "Authorize" button
3. Enter your token in the format: `Bearer YOUR_TOKEN_HERE`
4. Test the protected endpoints

## Example Workflow

1. **Add user** → Get token
2. **Login** → Verify token works
3. **Test** → Get timestamp (proves authentication)
4. **Logout** → End session
