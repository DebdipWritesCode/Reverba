from fastapi import APIRouter, Response, Cookie, HTTPException, status
from app.models.user import UserRegister, UserLogin, UserResponse, TokenResponse
from app.middleware.auth_middleware import get_current_user
from app.services.auth_service import (
    register_user, login_user, refresh_access_token, logout_user
)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister):
    """Register a new user"""
    return await register_user(user_data)

@router.post("/login", response_model=TokenResponse)
async def login(user_data: UserLogin, response: Response):
    """Login user and get access token"""
    return await login_user(user_data, response)

@router.post("/refresh", response_model=TokenResponse)
async def refresh(response: Response, refresh_token: str = Cookie(None)):
    """Refresh access token using refresh token from cookie"""
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found"
        )
    return await refresh_access_token(refresh_token, response)

@router.post("/logout")
async def logout(response: Response, refresh_token: str = Cookie(None)):
    """Logout user and invalidate refresh token"""
    return await logout_user(refresh_token, response)
