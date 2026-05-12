# 通知服务
"""
P2.3 实时数据：应用内通知的 CRUD + 偏好检查
"""
import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Notification, UserPreferences

logger = logging.getLogger(__name__)


class NotificationService:
    """通知服务（无状态单例，依赖注入 session）"""

    async def create_notification(
        self,
        session: AsyncSession,
        user_id: str,
        notification_type: str,
        title: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> Notification:
        notification = Notification(
            id=str(uuid.uuid4()),
            user_id=user_id,
            notification_type=notification_type,
            title=title,
            message=message,
            data=json.dumps(data or {}, ensure_ascii=False),
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        session.add(notification)
        await session.commit()
        await session.refresh(notification)
        return notification

    async def get_notifications(
        self,
        session: AsyncSession,
        user_id: str,
        unread_only: bool = False,
        limit: int = 20,
        offset: int = 0,
    ) -> Tuple[List[Notification], int]:
        q = select(Notification).where(Notification.user_id == user_id)
        count_q = select(func.count(Notification.id)).where(Notification.user_id == user_id)

        if unread_only:
            q = q.where(Notification.is_read == False)  # noqa: E712
            count_q = count_q.where(Notification.is_read == False)  # noqa: E712

        total = (await session.execute(count_q)).scalar() or 0
        q = q.order_by(Notification.created_at.desc()).offset(offset).limit(limit)
        result = await session.execute(q)
        notifications = list(result.scalars().all())
        return notifications, total

    async def mark_read(self, session: AsyncSession, notification_id: str, user_id: str) -> bool:
        result = await session.execute(
            select(Notification).where(
                Notification.id == notification_id,
                Notification.user_id == user_id,
            )
        )
        n = result.scalar_one_or_none()
        if n is None:
            return False
        n.is_read = True
        n.read_at = datetime.now(timezone.utc).isoformat()
        await session.commit()
        return True

    async def mark_all_read(self, session: AsyncSession, user_id: str) -> int:
        now = datetime.now(timezone.utc).isoformat()
        stmt = (
            update(Notification)
            .where(Notification.user_id == user_id, Notification.is_read == False)  # noqa: E712
            .values(is_read=True, read_at=now)
        )
        result = await session.execute(stmt)
        await session.commit()
        return result.rowcount

    async def get_unread_count(self, session: AsyncSession, user_id: str) -> int:
        q = select(func.count(Notification.id)).where(
            Notification.user_id == user_id,
            Notification.is_read == False,  # noqa: E712
        )
        return (await session.execute(q)).scalar() or 0

    async def delete_notification(self, session: AsyncSession, notification_id: str, user_id: str) -> bool:
        result = await session.execute(
            select(Notification).where(
                Notification.id == notification_id,
                Notification.user_id == user_id,
            )
        )
        n = result.scalar_one_or_none()
        if n is None:
            return False
        await session.delete(n)
        await session.commit()
        return True

    async def should_notify(self, session: AsyncSession, user_id: str, notification_type: str) -> bool:
        """检查用户通知偏好"""
        result = await session.execute(
            select(UserPreferences).where(UserPreferences.user_id == user_id)
        )
        prefs = result.scalar_one_or_none()
        if prefs is None:
            return True  # 没有偏好记录时默认通知

        try:
            settings = json.loads(prefs.notification_settings)
        except (json.JSONDecodeError, TypeError):
            return True

        if not settings.get("enabled", True):
            return False

        type_settings = settings.get("types", {})
        if notification_type in type_settings:
            return type_settings[notification_type]

        return True


# 全局单例
notification_service = NotificationService()
