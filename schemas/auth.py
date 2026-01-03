"""
Authentication schemas for request/response models.
"""
from pydantic import BaseModel, Field


class TokenRequest(BaseModel):
    """Request model for token generation."""
    username: str = Field(..., description="Username for authentication")
    password: str = Field(..., description="Password for authentication")


class TokenResponse(BaseModel):
    """Response model for token generation."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in minutes")

