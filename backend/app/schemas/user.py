from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base schema for user."""
    
    email: EmailStr = Field(..., description="User email")


class UserCreate(UserBase):
    """Schema for user creation."""
    
    password: str = Field(..., description="User password", min_length=8)
    role: str = Field("analyst", description="User role")


class UserLogin(BaseModel):
    """Schema for user login."""
    
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., description="User password")


class UserResponse(UserBase):
    """Schema for user response."""
    
    id: str = Field(..., description="User ID")
    role: str = Field(..., description="User role")
    
    class Config:
        orm_mode = True


class Token(BaseModel):
    """Schema for authentication token."""
    
    access_token: str = Field(..., description="Access token")
    token_type: str = Field(..., description="Token type")


class TokenData(BaseModel):
    """Schema for token data."""
    
    email: Optional[str] = Field(None, description="User email")
    role: Optional[str] = Field(None, description="User role")

