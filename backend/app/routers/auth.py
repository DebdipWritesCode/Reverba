from fastapi import APIRouter, Response, Cookie, HTTPException, status, Depends
from app.models.user import UserRegister, UserLogin, UserResponse, TokenResponse, ProfileUpdate, PasswordChange
from app.middleware.auth_middleware import get_current_user
from app.services.auth_service import (
    register_user, login_user, refresh_access_token, logout_user, update_profile, change_password
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

@router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    profile_data: ProfileUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update user profile (firstName and lastName)"""
    return await update_profile(current_user["user_id"], profile_data)

@router.put("/password")
async def change_user_password(
    password_data: PasswordChange,
    current_user: dict = Depends(get_current_user)
):
    """Change user password"""
    return await change_password(current_user["user_id"], password_data)
