from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from typing import Optional
import structlog
from datetime import datetime, timedelta

from app.core.security import (
    verify_password, get_password_hash, create_access_token, 
    create_refresh_token, verify_token, get_current_user, User
)
from app.core.database import get_db_connection, get_redis_client

logger = structlog.get_logger()
router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: str = "viewer"

@router.post("/login")
async def login(login_data: LoginRequest):
    """Authenticate user and return access token"""
    try:
        async with get_db_connection() as conn:
            # Get user from database
            user = await conn.fetchrow("""
                SELECT id, username, email, hashed_password, role, is_active
                FROM users
                WHERE username = $1
            """, login_data.username)
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials"
                )
            
            if not user["is_active"]:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User account is disabled"
                )
            
            # Verify password
            if not verify_password(login_data.password, user["hashed_password"]):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials"
                )
            
            # Update last login
            await conn.execute("""
                UPDATE users
                SET last_login = NOW()
                WHERE id = $1
            """, user["id"])
            
            # Create tokens
            token_data = {
                "sub": user["username"],
                "user_id": str(user["id"]),
                "role": user["role"]
            }
            
            access_token = create_access_token(token_data)
            refresh_token = create_refresh_token(token_data)
            
            # Store refresh token in Redis
            redis_client = await get_redis_client()
            await redis_client.setex(
                f"refresh_token:{user['id']}",
                7 * 24 * 3600,  # 7 days
                refresh_token
            )
            
            logger.info("User logged in successfully", username=user["username"])
            
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "expires_in": 30 * 60,  # 30 minutes
                "user": {
                    "id": str(user["id"]),
                    "username": user["username"],
                    "email": user["email"],
                    "role": user["role"]
                }
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Login failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@router.post("/refresh")
async def refresh_token(refresh_data: RefreshTokenRequest):
    """Refresh access token using refresh token"""
    try:
        # Verify refresh token
        token_data = verify_token(refresh_data.refresh_token)
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Check if refresh token exists in Redis
        redis_client = await get_redis_client()
        stored_token = await redis_client.get(f"refresh_token:{token_data.user_id}")
        
        if not stored_token or stored_token != refresh_data.refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Create new access token
        new_token_data = {
            "sub": token_data.username,
            "user_id": token_data.user_id,
            "role": token_data.role
        }
        
        access_token = create_access_token(new_token_data)
        
        logger.info("Token refreshed successfully", username=token_data.username)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": 30 * 60  # 30 minutes
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Token refresh failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """Logout user and invalidate tokens"""
    try:
        # Remove refresh token from Redis
        redis_client = await get_redis_client()
        await redis_client.delete(f"refresh_token:{current_user.id}")
        
        logger.info("User logged out successfully", username=current_user.username)
        
        return {"message": "Logged out successfully"}
        
    except Exception as e:
        logger.error("Logout failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )

@router.get("/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at.isoformat(),
        "last_login": current_user.last_login.isoformat() if current_user.last_login else None
    }

@router.post("/register")
async def register_user(user_data: UserCreate, current_user: User = Depends(get_current_user)):
    """Register a new user (admin only)"""
    try:
        # Check if current user is admin
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin role required"
            )
        
        # Validate role
        if user_data.role not in ["admin", "analyst", "viewer"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid role"
            )
        
        async with get_db_connection() as conn:
            # Check if username already exists
            existing_user = await conn.fetchrow("""
                SELECT id FROM users WHERE username = $1
            """, user_data.username)
            
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already exists"
                )
            
            # Check if email already exists
            existing_email = await conn.fetchrow("""
                SELECT id FROM users WHERE email = $1
            """, user_data.email)
            
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already exists"
                )
            
            # Hash password
            hashed_password = get_password_hash(user_data.password)
            
            # Create user
            user_id = await conn.fetchval("""
                INSERT INTO users (username, email, hashed_password, role)
                VALUES ($1, $2, $3, $4)
                RETURNING id
            """, user_data.username, user_data.email, hashed_password, user_data.role)
            
            logger.info("User registered successfully", username=user_data.username, role=user_data.role)
            
            return {
                "message": "User registered successfully",
                "user_id": str(user_id),
                "username": user_data.username,
                "email": user_data.email,
                "role": user_data.role
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error("User registration failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User registration failed"
        )

@router.get("/users")
async def get_users(current_user: User = Depends(get_current_user)):
    """Get all users (admin only)"""
    try:
        # Check if current user is admin
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin role required"
            )
        
        async with get_db_connection() as conn:
            users = await conn.fetch("""
                SELECT id, username, email, role, is_active, created_at, last_login
                FROM users
                ORDER BY created_at DESC
            """)
            
            return {
                "users": [
                    {
                        "id": str(user["id"]),
                        "username": user["username"],
                        "email": user["email"],
                        "role": user["role"],
                        "is_active": user["is_active"],
                        "created_at": user["created_at"].isoformat(),
                        "last_login": user["last_login"].isoformat() if user["last_login"] else None
                    }
                    for user in users
                ],
                "total": len(users)
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get users", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get users"
        )

@router.put("/users/{user_id}/status")
async def update_user_status(
    user_id: str,
    status_data: dict,
    current_user: User = Depends(get_current_user)
):
    """Update user status (admin only)"""
    try:
        # Check if current user is admin
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin role required"
            )
        
        is_active = status_data.get("is_active")
        if is_active is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="is_active field is required"
            )
        
        async with get_db_connection() as conn:
            result = await conn.execute("""
                UPDATE users
                SET is_active = $1
                WHERE id = $2
            """, is_active, user_id)
            
            if result == "UPDATE 0":
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # If deactivating user, remove their refresh token
            if not is_active:
                redis_client = await get_redis_client()
                await redis_client.delete(f"refresh_token:{user_id}")
            
            logger.info("User status updated", user_id=user_id, is_active=is_active)
            
            return {"message": "User status updated successfully"}
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update user status", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user status"
        ) 