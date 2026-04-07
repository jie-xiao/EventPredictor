# EventPredictor 认证服务
import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional, Tuple

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User, UserSession, UserPreferences
from app.core.security import (
    hash_password, verify_password,
    create_access_token, create_refresh_token, decode_token
)
from app.core.config import config


class AuthService:
    """认证服务：注册、登录、刷新、登出"""

    async def register(
        self, session: AsyncSession, username: str, email: str, password: str
    ) -> User:
        """注册新用户"""
        # 检查用户名唯一性
        result = await session.execute(select(User).where(User.username == username))
        if result.scalar_one_or_none():
            raise ValueError("Username already exists")

        # 检查邮箱唯一性
        result = await session.execute(select(User).where(User.email == email))
        if result.scalar_one_or_none():
            raise ValueError("Email already exists")

        # 创建用户
        user = User(
            id=str(uuid.uuid4()),
            username=username,
            email=email,
            hashed_password=hash_password(password),
            display_name=username,
            is_active=True,
        )
        session.add(user)

        # 创建默认偏好
        prefs = UserPreferences(user_id=user.id)
        session.add(prefs)

        await session.commit()
        await session.refresh(user)
        return user

    async def login(
        self, session: AsyncSession, username: str, password: str, device_info: str = "", ip_address: str = ""
    ) -> Tuple[User, str, str]:
        """登录，返回 (user, access_token, refresh_token)"""
        # 查找用户
        result = await session.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()

        if not user or not verify_password(password, user.hashed_password):
            raise ValueError("Invalid username or password")

        if not user.is_active:
            raise ValueError("Account is deactivated")

        # 生成 token
        access_token = create_access_token(user.id, user.username)
        refresh_token = create_refresh_token(user.id)

        # 保存 refresh token 到数据库
        expires_at = (
            datetime.now(timezone.utc) + timedelta(days=config.auth.refresh_token_expire_days)
        ).isoformat()
        user_session = UserSession(
            id=str(uuid.uuid4()),
            user_id=user.id,
            refresh_token=refresh_token,
            device_info=device_info,
            ip_address=ip_address,
            expires_at=expires_at,
        )
        session.add(user_session)

        # 更新最后登录时间
        user.last_login_at = datetime.now(timezone.utc).isoformat()
        await session.commit()

        return user, access_token, refresh_token

    async def refresh(
        self, session: AsyncSession, refresh_token: str
    ) -> Tuple[str, str]:
        """刷新 token，返回新的 (access_token, refresh_token)"""
        # 解码 refresh token
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise ValueError("Invalid refresh token")

        user_id = payload.get("sub")

        # 查找有效的 session
        result = await session.execute(
            select(UserSession).where(
                and_(
                    UserSession.refresh_token == refresh_token,
                    UserSession.revoked_at.is_(None),
                )
            )
        )
        user_session = result.scalar_one_or_none()
        if not user_session:
            raise ValueError("Refresh token not found or already revoked")

        # 检查过期
        expires_dt = datetime.fromisoformat(user_session.expires_at)
        if expires_dt < datetime.now(timezone.utc):
            raise ValueError("Refresh token expired")

        # 验证用户仍有效
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user or not user.is_active:
            raise ValueError("User not found or inactive")

        # 撤销旧 refresh token（rotation）
        user_session.revoked_at = datetime.now(timezone.utc).isoformat()

        # 生成新 token
        new_access = create_access_token(user.id, user.username)
        new_refresh = create_refresh_token(user.id)

        # 保存新 refresh token
        new_expires = (
            datetime.now(timezone.utc) + timedelta(days=config.auth.refresh_token_expire_days)
        ).isoformat()
        new_session = UserSession(
            id=str(uuid.uuid4()),
            user_id=user.id,
            refresh_token=new_refresh,
            expires_at=new_expires,
        )
        session.add(new_session)
        await session.commit()

        return new_access, new_refresh

    async def logout(self, session: AsyncSession, refresh_token: str) -> None:
        """登出，撤销 refresh token"""
        result = await session.execute(
            select(UserSession).where(
                and_(
                    UserSession.refresh_token == refresh_token,
                    UserSession.revoked_at.is_(None),
                )
            )
        )
        user_session = result.scalar_one_or_none()
        if user_session:
            user_session.revoked_at = datetime.now(timezone.utc).isoformat()
            await session.commit()

    async def get_user_by_id(
        self, session: AsyncSession, user_id: str
    ) -> Optional[User]:
        """根据 ID 获取用户"""
        result = await session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()


# 全局实例
auth_service = AuthService()
