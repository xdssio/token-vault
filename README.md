<p align="center">
   <img src="https://raw.githubusercontent.com/xdssio/token-vault/main/docs/images/logo.png" alt="logo" width="400" />
</p>

# TokenVault

[![PyPI version](https://badge.fury.io/py/tokenvault.svg)](https://badge.fury.io/py/tokenvault)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/xdssio/token-vault/actions/workflows/ci.yml/badge.svg)](https://github.com/xdssio/token-vault/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/xdssio/token-vault/branch/main/graph/badge.svg)](https://codecov.io/gh/xdssio/token-vault)

TokenVault is a lightweight package for secure user management using encrypted tokens stored in a single file with asymmetric encryption.

## Features

- **Secure token storage** - All tokens and metadata encrypted in a single file
- **Asymmetric encryption** - Even if the file is compromised, tokens remain secure
- **Git-friendly** - Version control your user data with full encryption
- **No database required** - Perfect for POCs, prototypes, and small applications
- **CLI management** - Easy user management via command line
- **FastAPI integration** - Drop-in authentication for FastAPI applications


## Rationale

Why use **TokenVault** instead of a full identity provider or custom server?

- **Lightweight & Serverless** – No need to deploy or maintain a user management service. Your entire user/token state lives in a single encrypted file.  
- **Git/Data-Versioning Friendly** – The vault is just a file, so it fits naturally into repositories and data-versioning workflows (Git, DVC, etc.). You can track user changes, review access control in pull requests, and roll back if needed.  
- **Cost-Free** – Avoid recurring bills from external identity providers (e.g., Cognito, Auth0). TokenVault is free and open source.  
- **Ideal for Prototypes & Private APIs** – Quickly make an app private with API keys, managed in Git alongside code. Perfect for early-stage projects, POCs, and internal tools.  
- **Team Sharing with Security** – Share access securely by distributing only the encrypted vault and a password or environment variable. Even if the file leaks, tokens remain protected.  
- **Drop-in Authentication** – FastAPI integration makes it simple to secure endpoints without spinning up a separate auth microservice.  

### When to Use

Use **TokenVault** when you want to:  
- Secure internal APIs without adding heavy dependencies.  
- Manage small to medium sets of users directly in Git.  
- Version-control user & metadata updates with **data-versioning tools**.  
- Keep prototypes and POCs simple but secure.  
- Avoid vendor lock-in and recurring SaaS costs for identity management.  


## Installation

```bash
pip install tokenvault
```

## Quick Start

```python
from tokenvault import TokenVault

# Create vault and add user
vault = TokenVault()
token = vault.add("user@example.com", metadata={"name": "John Doe", "role": "admin"})

# Validate token
user_data = vault.validate(token)
print(user_data)  # {'name': 'John Doe', 'role': 'admin'}

# Save vault
vault.save("vault.db")

# Load vault
loaded_vault = TokenVault("vault.db")
loaded_vault.validate(token)  # {'name': 'John Doe', 'role': 'admin'}
```

## Encryption

For enhanced security, encrypt your vault with a password:

```python
import os
from tokenvault import TokenVault

vault = TokenVault()
token = vault.add("user@example.com", metadata={"name": "John Doe"})

# Generate and save with password
password = vault.generate_key()
vault.save("vault.db", password=password)

# Load with password
TokenVault("vault.db", password=password).validate(token)

# Or picked-up automatically from environment variable
os.environ['TOKENVAULT_PASSWORD'] = password
TokenVault("vault.db").validate(token)
```

## CLI Usage

Manage users via command line:

```bash
# Initialize vault (unencrypted by default)
$ tv init vault.db
Vault created at vault.db and not encrypted

# Add user (token copied to clipboard)
$ tv add user@example.com vault.db --metadata='{"role": "admin", "name": "John Doe"}'

# List users
$ tv list vault.db
user@example.com

# Validate token
$ tv validate <token> vault.db
{"role": "admin", "name": "John Doe"}

# Remove user
$ tv remove user@example.com vault.db

# Create vault with generated password
$ tv init vault.db --generate-password
Generated password (copied to clipboard): G99********
Vault created at vault.db and encrypted with password

# Or use a specific password
$ tv init vault.db --password "your-secret-password"
Vault created at vault.db and encrypted with password

# Set environment variable for subsequent commands
$ export TOKENVAULT_PASSWORD=G99********

# Add user (password picked up from environment)
$ tv add user@example.com vault.db
```

## FastAPI Integration

Secure your FastAPI endpoints with TokenVault. See the [examples/](examples/) directory for a complete working demo.

```python
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from tokenvault import TokenVault

app = FastAPI()
security = HTTPBearer()
vault = TokenVault("vault.db")

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
```

### Usage Example

```bash
# Add user and get token
$ tv add user@example.com vault.db --metadata='{"role": "admin", "name": "John Doe"}'

# Make authenticated requests
$ curl -H "Authorization: Bearer <token>" http://localhost:8000/protected
{"message": "Access granted", "user": {"role": "admin", "name": "John Doe"}}

# Public endpoints work without authentication
$ curl http://localhost:8000/public
{"message": "This is a public endpoint"}
```

## Security

For security best practices, vulnerability reporting, and known limitations, see [SECURITY.md](SECURITY.md).

## Use with Care ⚠️

TokenVault is a **pet project**, built to simplify small-scale, secure user management.  
While it provides encryption and safe defaults, it is **not a replacement** for enterprise-grade identity management solutions (e.g., Cognito, Auth0, Keycloak).  

Use it with care in:  
- Personal projects  
- Internal tools  
- Prototypes & proofs-of-concept  
- Small teams that benefit from Git-based user/version control  

Avoid using it for:  
- Applications with large user bases  
- Systems requiring strict compliance (HIPAA, GDPR, SOC2, etc.)  
- High-security production environments where professional solutions are required  