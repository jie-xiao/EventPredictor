"""EventPredictor User API Routes"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_session
from app.db.models import User, Favorite, AnalysisHistory
from app.services.user_service import user_service
from app.core.auth_deps import get_current_user

router = APIRouter(prefix="/api/v1/users", tags=["Users"])


# --- Request/Response Models ---

class ProfileUpdateRequest(BaseModel):
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None


class PreferencesUpdateRequest(BaseModel):
    default_roles: Optional[list] = None
    default_depth: Optional[str] = None
    default_language: Optional[str] = None
    theme: Optional[str] = None


class FavoriteRequest(BaseModel):
    analysis_id: str
    notes: str = ""
    folder: str = "default"


class FavoriteResponse(BaseModel):
    id: str
    analysis_id: str
    notes: str
    folder: str
    created_at: str


class AnalysisHistoryResponse(BaseModel):
    id: str
    event_id: str
    event_title: str
    category: str
    analysis_type: str
    overall_confidence: float
    trend: Optional[str] = None
    created_at: str


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    display_name: str
    avatar_url: Optional[str] = None


# --- Profile Endpoints ---

@router.put("/me/profile", response_model=UserResponse)
async def update_profile(
    req: ProfileUpdateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """Update user profile"""
    try:
        updated = await user_service.update_profile(
            db, user.id,
            display_name=req.display_name,
            avatar_url=req.avatar_url,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return UserResponse(
        id=updated.id,
        username=updated.username,
        email=updated.email,
        display_name=updated.display_name,
        avatar_url=updated.avatar_url,
    )


@router.get("/me/preferences")
async def get_preferences(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """Get user preferences"""
    return await user_service.get_preferences(db, user.id)


@router.put("/me/preferences")
async def update_preferences(
    req: PreferencesUpdateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """Update user preferences"""
    return await user_service.update_preferences(db, user.id, **req.dict(exclude_none=True))


# --- Favorites Endpoints ---

@router.get("/me/favorites")
async def list_favorites(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    folder: Optional[str] = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """List user favorites"""
    favorites, total = await user_service.list_favorites(
        db, user.id, limit=limit, offset=offset, folder=folder
    )
    return {
        "favorites": [
            FavoriteResponse(
                id=f.id, analysis_id=f.analysis_id,
                notes=f.notes, folder=f.folder, created_at=f.created_at,
            ) for f in favorites
        ],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.post("/me/favorites", status_code=201)
async def add_favorite(
    req: FavoriteRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """Add to favorites"""
    try:
        fav = await user_service.add_favorite(
            db, user.id, req.analysis_id, notes=req.notes, folder=req.folder
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"id": fav.id, "message": "Added to favorites"}


@router.delete("/me/favorites/{analysis_id}")
async def remove_favorite(
    analysis_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """Remove from favorites"""
    removed = await user_service.remove_favorite(db, user.id, analysis_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Favorite not found")
    return {"message": "Removed from favorites"}


# --- History Endpoints ---

@router.get("/me/history")
async def get_history(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    category: Optional[str] = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """Get user analysis history"""
    records, total = await user_service.get_analysis_history(
        db, user.id, limit=limit, offset=offset, category=category
    )
    return {
        "records": [
            AnalysisHistoryResponse(
                id=r.id, event_id=r.event_id, event_title=r.event_title,
                category=r.category, analysis_type=r.analysis_type,
                overall_confidence=r.overall_confidence, trend=r.trend,
                created_at=r.created_at,
            ) for r in records
        ],
        "total": total,
        "limit": limit,
        "offset": offset,
    }
