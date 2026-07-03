"""Simple JWT authentication for hermes-gw.

Users are hardcoded and mapped to Hermes profile names.
Token validation extracts user_id which drives gateway routing.
"""

import os
from typing import Optional

import jwt
from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

JWT_SECRET = os.environ.get("JWT_SECRET", "dev-secret-change-me")
JWT_ALGORITHM = "HS256"

# Hardcoded users -> Hermes profile names
USERS: dict[str, str] = {
    "isaac": "user-isaac",
    "miguel": "user-miguel",
    "pablo": "user-pablo",
}

security = HTTPBearer(auto_error=False)


def validate_token(token: str) -> dict:
    """Validate a JWT and return the decoded payload.

    Raises HTTPException with 401 if the token is invalid or expired.
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = payload.get("sub")
    if not user_id or user_id not in USERS:
        raise HTTPException(status_code=401, detail="Unknown user")

    return {"user_id": user_id, "profile": USERS[user_id]}


async def get_current_user(request: Request) -> dict:
    """FastAPI dependency that extracts and validates the JWT from the request.

    Looks for the token in the Authorization header (Bearer scheme) first,
    then falls back to the 'token' query parameter for SSE compatibility.
    """
    # Try Authorization header first
    credentials: Optional[HTTPAuthorizationCredentials] = await security(request)
    if credentials:
        token = credentials.credentials
    else:
        # Fallback to query parameter (needed for EventSource / SSE clients)
        token = request.query_params.get("token")

    if not token:
        raise HTTPException(status_code=401, detail="Missing authentication token")

    return validate_token(token)


def create_token(user_id: str) -> str:
    """Create a JWT for the given user_id.

    Useful for testing and bootstrapping. Not exposed as an API endpoint
    in production — use your identity provider instead.
    """
    if user_id not in USERS:
        raise ValueError(f"Unknown user: {user_id}")
    return jwt.encode({"sub": user_id}, JWT_SECRET, algorithm=JWT_ALGORITHM)
