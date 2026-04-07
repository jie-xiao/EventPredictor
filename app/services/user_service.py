import json
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Tuple

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User, UserPreferences, Favorite, AnalysisHistory


class UserService:

    async def update_profile(
        self,
        db: AsyncSession,
        user_id: str,
        display_name: Optional[str] = None,
        avatar_url: Optional[str] = None,
    ) -> User:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise ValueError("User not found")
        if display_name is not None:
            user.display_name = display_name
        if avatar_url is not None:
            user.avatar_url = avatar_url
        user.updated_at = datetime.now(timezone.utc).isoformat()
        await db.commit()
        await db.refresh(user)
        return user

    async def get_preferences(self, db: AsyncSession, user_id: str) -> dict:
        result = await db.execute(
            select(UserPreferences).where(UserPreferences.user_id == user_id)
        )
        prefs = result.scalar_one_or_none()
        if not prefs:
            prefs = UserPreferences(user_id=user_id)
            db.add(prefs)
            await db.commit()
            await db.refresh(prefs)
        return {
            "default_roles": json.loads(prefs.default_roles),
            "default_depth": prefs.default_depth,
            "default_language": prefs.default_language,
            "theme": prefs.theme,
            "notification_settings": json.loads(prefs.notification_settings),
            "dashboard_layout": json.loads(prefs.dashboard_layout),
        }

    async def update_preferences(self, db: AsyncSession, user_id: str, **kwargs) -> dict:
        result = await db.execute(
            select(UserPreferences).where(UserPreferences.user_id == user_id)
        )
        prefs = result.scalar_one_or_none()
        if not prefs:
            prefs = UserPreferences(user_id=user_id)
            db.add(prefs)
        if "default_roles" in kwargs:
            prefs.default_roles = json.dumps(kwargs["default_roles"])
        if "default_depth" in kwargs:
            prefs.default_depth = kwargs["default_depth"]
        if "default_language" in kwargs:
            prefs.default_language = kwargs["default_language"]
        if "theme" in kwargs:
            prefs.theme = kwargs["theme"]
        if "notification_settings" in kwargs:
            prefs.notification_settings = json.dumps(kwargs["notification_settings"])
        if "dashboard_layout" in kwargs:
            prefs.dashboard_layout = json.dumps(kwargs["dashboard_layout"])
        prefs.updated_at = datetime.now(timezone.utc).isoformat()
        await db.commit()
        await db.refresh(prefs)
        return await self.get_preferences(db, user_id)

    async def add_favorite(
        self, db: AsyncSession, user_id: str, analysis_id: str,
        notes: str = "", folder: str = "default",
    ) -> Favorite:
        fav = Favorite(
            id=str(uuid.uuid4()),
            user_id=user_id,
            analysis_id=analysis_id,
            notes=notes,
            folder=folder,
        )
        db.add(fav)
        await db.commit()
        await db.refresh(fav)
        return fav

    async def remove_favorite(self, db: AsyncSession, user_id: str, analysis_id: str) -> bool:
        result = await db.execute(
            select(Favorite).where(
                Favorite.user_id == user_id,
                Favorite.analysis_id == analysis_id,
            )
        )
        fav = result.scalar_one_or_none()
        if fav:
            await db.delete(fav)
            await db.commit()
            return True
        return False

    async def list_favorites(
        self, db: AsyncSession, user_id: str,
        limit: int = 20, offset: int = 0,
        folder: Optional[str] = None,
    ) -> Tuple[List[Favorite], int]:
        query = select(Favorite).where(Favorite.user_id == user_id)
        if folder:
            query = query.where(Favorite.folder == folder)
        count_q = select(func.count()).select_from(query.subquery())
        total = (await db.execute(count_q)).scalar() or 0
        query = query.order_by(Favorite.created_at.desc()).offset(offset).limit(limit)
        result = await db.execute(query)
        favorites = list(result.scalars().all())
        return favorites, total

    async def get_analysis_history(
        self, db: AsyncSession, user_id: str,
        limit: int = 20, offset: int = 0,
        category: Optional[str] = None,
    ) -> Tuple[List[AnalysisHistory], int]:
        query = select(AnalysisHistory).where(AnalysisHistory.user_id == user_id)
        if category:
            query = query.where(AnalysisHistory.category == category)
        count_q = select(func.count()).select_from(query.subquery())
        total = (await db.execute(count_q)).scalar() or 0
        query = query.order_by(AnalysisHistory.created_at.desc()).offset(offset).limit(limit)
        result = await db.execute(query)
        records = list(result.scalars().all())
        return records, total


user_service = UserService()
