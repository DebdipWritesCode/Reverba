from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# Request Models
class UserRegister(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Response Models
class UserResponse(BaseModel):
    id: str
    email: str
    isActive: bool
    createdAt: datetime
    lastLoginAt: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Token Models
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    email: str
