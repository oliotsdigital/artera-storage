"""
Router for authentication operations.
"""
import os
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer
from schemas.auth import TokenRequest, TokenResponse
from services.auth_service import create_access_token, JWT_ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()
security = HTTPBearer()


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Login / Get Access Token",
    description="""
    Authenticate and receive a JWT access token.
    
    **Note:** This is a simple authentication endpoint. In production, you should:
    - Validate credentials against a database
    - Use password hashing (bcrypt)
    - Implement user management
    
    **Current Implementation:**
    - Accepts any username/password combination
    - Returns a JWT token valid for 24 hours (configurable via JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    - Token must be included in Authorization header: `Bearer <token>`
    
    **Usage:**
    1. Call this endpoint with username and password
    2. Copy the `access_token` from the response
    3. Include it in subsequent API requests: `Authorization: Bearer <token>`
    """,
    responses={
        200: {
            "description": "Authentication successful, token returned",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer",
                        "expires_in": 1440
                    }
                }
            }
        },
        401: {"description": "Invalid credentials"}
    },
    tags=["authentication"]
)
async def login(request: TokenRequest):
    """
    Login endpoint to get JWT access token.
    
    In a production environment, you should validate credentials against a database.
    For now, this accepts any username/password and generates a token.
    """
    # TODO: In production, validate credentials against database
    # For now, accept any username/password
    username = request.username
    password = request.password
    
    # Basic validation (in production, check against database)
    if not username or not password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username and password are required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create token with user information
    # In production, you would fetch user_id from database
    token_data = {
        "sub": username,  # Subject (user identifier)
        "username": username,
        "user_id": username,  # In production, use actual user ID from database
    }
    
    access_token = create_access_token(data=token_data)
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )


@router.get(
    "/verify",
    status_code=status.HTTP_200_OK,
    summary="Verify Token",
    description="""
    Verify if the current JWT token is valid.
    
    Returns the decoded token payload if valid.
    """,
    tags=["authentication"]
)
async def verify_token_endpoint(current_user: dict = Depends(security)):
    """
    Verify token endpoint - returns current user information from token.
    """
    return {
        "valid": True,
        "user": current_user,
        "message": "Token is valid"
    }

