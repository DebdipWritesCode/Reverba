from datetime import datetime, timedelta
from bson import ObjectId
from fastapi import HTTPException, status, Response
from app.database import get_users_collection, get_refresh_tokens_collection
from app.models.user import UserRegister, UserLogin
from app.utils.password_handler import hash_password, verify_password, hash_token
from app.utils.jwt_handler import create_access_token, create_refresh_token, verify_refresh_token
from app.settings.get_env import REFRESH_TOKEN_EXPIRE_DAYS

async def register_user(user_data: UserRegister) -> dict:
    """Register a new user"""
    users_collection = get_users_collection()
    
    # Check if user already exists
    existing_user = await users_collection.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user document
    user_doc = {
        "email": user_data.email,
        "passwordHash": hash_password(user_data.password),
        "firstName": user_data.firstName,
        "lastName": user_data.lastName,
        "isActive": True,
        "createdAt": datetime.utcnow(),
        "lastLoginAt": None
    }
    
    result = await users_collection.insert_one(user_doc)
    user_doc["_id"] = result.inserted_id
    
    return {
        "id": str(user_doc["_id"]),
        "email": user_doc["email"],
        "firstName": user_doc["firstName"],
        "lastName": user_doc["lastName"],
        "isActive": user_doc["isActive"],
        "createdAt": user_doc["createdAt"],
        "lastLoginAt": user_doc["lastLoginAt"]
    }

async def login_user(user_data: UserLogin, response: Response) -> dict:
    """Login user and get access token"""
    users_collection = get_users_collection()
    
    # Find user by email
    user = await users_collection.find_one({"email": user_data.email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(user_data.password, user["passwordHash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Check if user is active
    if not user.get("isActive", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Update last login
    await users_collection.update_one(
        {"_id": user["_id"]},
        {"$set": {"lastLoginAt": datetime.utcnow()}}
    )
    
    # Create tokens
    access_token = create_access_token(data={"sub": str(user["_id"])})
    refresh_token = create_refresh_token(data={"sub": str(user["_id"])})
    
    # Hash and store refresh token
    refresh_tokens_collection = get_refresh_tokens_collection()
    token_hash = hash_token(refresh_token)
    expires_at = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    await refresh_tokens_collection.insert_one({
        "userId": user["_id"],
        "tokenHash": token_hash,
        "expiresAt": expires_at,
        "revoked": False,
        "createdAt": datetime.utcnow()
    })
    
    # Set refresh token in HTTP-only cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "email": user["email"],
        "firstName": user.get("firstName", ""),
        "lastName": user.get("lastName", "")
    }

async def refresh_access_token(refresh_token: str, response: Response) -> dict:
    """Refresh access token using refresh token"""
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not provided"
        )
    
    # Verify refresh token
    payload = verify_refresh_token(refresh_token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    # Check if refresh token exists in database
    refresh_tokens_collection = get_refresh_tokens_collection()
    token_hash = hash_token(refresh_token)
    
    token_doc = await refresh_tokens_collection.find_one({
        "userId": ObjectId(user_id),
        "tokenHash": token_hash,
        "revoked": False
    })
    
    if not token_doc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found or revoked"
        )
    
    # Check if token is expired
    if token_doc["expiresAt"] < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired"
        )
    
    # Get user
    users_collection = get_users_collection()
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if not user or not user.get("isActive", True):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Create new access token
    access_token = create_access_token(data={"sub": str(user["_id"])})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "email": user["email"],
        "firstName": user.get("firstName", ""),
        "lastName": user.get("lastName", "")
    }

async def logout_user(refresh_token: str, response: Response) -> dict:
    """Logout user and revoke refresh token"""
    if not refresh_token:
        return {"message": "Already logged out"}
    
    # Hash token and find it in database
    refresh_tokens_collection = get_refresh_tokens_collection()
    token_hash = hash_token(refresh_token)
    
    # Revoke token
    result = await refresh_tokens_collection.update_one(
        {"tokenHash": token_hash, "revoked": False},
        {"$set": {"revoked": True}}
    )
    
    # Clear cookie
    response.delete_cookie(key="refresh_token")
    
    return {"message": "Logged out successfully"}
