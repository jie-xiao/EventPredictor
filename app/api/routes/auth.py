"""EventPredictor Authentication API Routes"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_session
from app.db.models import User
from app.services.auth_service import auth_service
from app.core.auth_deps import get_current_user

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


# --- Request/Response Models ---

class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    display_name: str
    avatar_url: str | None = None
    is_active: bool
    created_at: str
    last_login_at: str | None = None


class RefreshRequest(BaseModel):
    refresh_token: str


def _user_to_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        display_name=user.display_name,
        avatar_url=user.avatar_url,
        is_active=user.is_active,
        created_at=user.created_at,
        last_login_at=user.last_login_at,
    )


# --- Endpoints ---

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_session)):
    """User registration"""
    try:
        user = await auth_service.register(db, req.username, req.email, req.password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    _, access_token, refresh_token = await auth_service.login(db, req.username, req.password)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_session)):
    """User login"""
    try:
        user, access_token, refresh_token = await auth_service.login(db, req.username, req.password)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(req: RefreshRequest, db: AsyncSession = Depends(get_session)):
    """Refresh access token"""
    try:
        access_token, refresh_token = await auth_service.refresh(db, req.refresh_token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)):
    """Get current user profile"""
    return _user_to_response(user)


@router.post("/logout")
async def logout(
    req: RefreshRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """Logout and revoke refresh token"""
    await auth_service.logout(db, req.refresh_token)
    return {"message": "Logged out successfully"}
