# 通知 API 路由
"""
P2.3 实时数据：通知 CRUD 端点
"""
import json

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_session
from app.core.auth_deps import get_current_user
from app.db.models import User
from app.services.notification_service import notification_service

router = APIRouter(prefix="/api/v1/notifications", tags=["notifications"])


class NotificationResponse(BaseModel):
    id: str
    notification_type: str
    title: str
    message: str
    data: dict
    is_read: bool
    created_at: str
    read_at: str | None = None

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    notifications: list[NotificationResponse]
    total: int
    unread_count: int


class UnreadCountResponse(BaseModel):
    unread_count: int


class MarkReadResponse(BaseModel):
    success: bool


class MarkAllReadResponse(BaseModel):
    marked_count: int


def _to_response(n) -> NotificationResponse:
    data = {}
    try:
        data = json.loads(n.data) if n.data else {}
    except (json.JSONDecodeError, TypeError):
        pass
    return NotificationResponse(
        id=n.id,
        notification_type=n.notification_type,
        title=n.title,
        message=n.message,
        data=data,
        is_read=n.is_read,
        created_at=n.created_at,
        read_at=n.read_at,
    )


@router.get("", response_model=NotificationListResponse)
async def list_notifications(
    unread_only: bool = Query(False, description="Only return unread notifications"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    notifications, total = await notification_service.get_notifications(
        session, user.id, unread_only=unread_only, limit=limit, offset=offset
    )
    unread_count = await notification_service.get_unread_count(session, user.id)
    return NotificationListResponse(
        notifications=[_to_response(n) for n in notifications],
        total=total,
        unread_count=unread_count,
    )


@router.get("/unread-count", response_model=UnreadCountResponse)
async def get_unread_count(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    count = await notification_service.get_unread_count(session, user.id)
    return UnreadCountResponse(unread_count=count)


@router.post("/{notification_id}/read", response_model=MarkReadResponse)
async def mark_notification_read(
    notification_id: str,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    success = await notification_service.mark_read(session, notification_id, user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")
    return MarkReadResponse(success=True)


@router.post("/mark-all-read", response_model=MarkAllReadResponse)
async def mark_all_notifications_read(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    count = await notification_service.mark_all_read(session, user.id)
    return MarkAllReadResponse(marked_count=count)


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: str,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    success = await notification_service.delete_notification(session, notification_id, user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"success": True}
