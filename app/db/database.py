# EventPredictor 数据库引擎和会话管理
import os
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator

# 数据库文件路径
DB_DIR = os.path.join(Path(__file__).parent.parent.parent, "data")
DB_PATH = os.path.join(DB_DIR, "eventpredictor.db")
DB_URL = f"sqlite+aiosqlite:///{DB_PATH}"


class Base(DeclarativeBase):
    """SQLAlchemy 声明式基类"""
    pass


# 全局引擎和会话工厂（延迟初始化）
_engine = None
_session_factory = None


async def init_db() -> None:
    """初始化数据库引擎并创建所有表"""
    global _engine, _session_factory

    # 确保数据目录存在
    os.makedirs(DB_DIR, exist_ok=True)

    _engine = create_async_engine(
        DB_URL,
        echo=False,
        pool_pre_ping=True,
    )

    _session_factory = async_sessionmaker(
        _engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    # 创建所有表
    async with _engine.begin() as conn:
        # 导入所有模型以确保它们被注册
        from app.db import models  # noqa: F401
        await conn.run_sync(Base.metadata.create_all)

    print(f"Database initialized: {DB_PATH}")


async def cleanup_db() -> None:
    """关闭数据库引擎"""
    global _engine, _session_factory
    if _engine:
        await _engine.dispose()
        _engine = None
        _session_factory = None
        print("Database connection closed")


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话（用于 FastAPI 依赖注入）"""
    if _session_factory is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    async with _session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """获取会话工厂（用于服务层直接获取会话）"""
    if _session_factory is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return _session_factory
