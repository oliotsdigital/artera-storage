"""
Router for authentication operations.
"""
from fastapi import APIRouter, HTTPException, status, Depends
from schemas.auth import TokenRequest, TokenResponse
from services.auth_service import create_access_token, get_current_user, JWT_ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Login / Get Access Token",
    description="""
    Authenticate and receive a JWT access token.
    
    **Implementation:**
    - Accepts username and password
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
    Accepts username and password and returns a JWT token.
    """
    username = request.username
    password = request.password
    
    # Basic validation
    if not username or not password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username and password are required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create token with user information
    token_data = {
        "sub": username,
        "username": username,
        "user_id": username,
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
async def verify_token_endpoint(current_user: dict = Depends(get_current_user)):
    """
    Verify token endpoint - returns current user information from token.
    """
    return {
        "valid": True,
        "user": current_user,
        "message": "Token is valid"
    }

