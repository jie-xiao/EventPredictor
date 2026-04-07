# EventPredictor ORM 模型定义
import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Text, Integer, Float, Boolean, ForeignKey, Index, UniqueConstraint
)
from sqlalchemy.orm import relationship
from app.db.database import Base


def _generate_id() -> str:
    return str(uuid.uuid4())


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ─────────────── 用户表 ───────────────
class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=_generate_id)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    display_name = Column(String(100), nullable=False, default="")
    avatar_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(String, nullable=False, default=_now)
    updated_at = Column(String, nullable=False, default=_now)
    last_login_at = Column(String, nullable=True)

    # 关系
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    preferences = relationship("UserPreferences", back_populates="user", uselist=False, cascade="all, delete-orphan")
    favorites = relationship("Favorite", back_populates="user", cascade="all, delete-orphan")
    shared_reports = relationship("SharedReport", back_populates="owner", cascade="all, delete-orphan")
    owned_workspaces = relationship("Workspace", back_populates="owner", cascade="all, delete-orphan")
    workspace_memberships = relationship("WorkspaceMember", back_populates="user", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="user", cascade="all, delete-orphan")
    analysis_records = relationship("AnalysisHistory", back_populates="user")


class UserSession(Base):
    __tablename__ = "user_sessions"

    id = Column(String, primary_key=True, default=_generate_id)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    refresh_token = Column(String, unique=True, nullable=False, index=True)
    device_info = Column(String(500), nullable=False, default="")
    ip_address = Column(String(50), nullable=False, default="")
    expires_at = Column(String, nullable=False)
    created_at = Column(String, nullable=False, default=_now)
    revoked_at = Column(String, nullable=True)

    user = relationship("User", back_populates="sessions")


class UserPreferences(Base):
    __tablename__ = "user_preferences"

    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    default_roles = Column(Text, nullable=False, default="[]")          # JSON array
    default_depth = Column(String(20), nullable=False, default="standard")
    default_language = Column(String(10), nullable=False, default="zh-CN")
    theme = Column(String(20), nullable=False, default="dark")
    notification_settings = Column(Text, nullable=False, default="{}")  # JSON
    dashboard_layout = Column(Text, nullable=False, default="{}")       # JSON
    updated_at = Column(String, nullable=False, default=_now)

    user = relationship("User", back_populates="preferences")


# ─────────────── 分析历史 ───────────────
class AnalysisHistory(Base):
    __tablename__ = "analysis_history"

    id = Column(String, primary_key=True, default=lambda: f"pred_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}")
    user_id = Column(String, ForeignKey("users.id"), nullable=True, index=True)
    event_id = Column(String, nullable=False, index=True)
    event_title = Column(String(500), nullable=False)
    event_description = Column(Text, nullable=False, default="")
    category = Column(String(50), nullable=False, default="Other")
    analysis_type = Column(String(30), nullable=False, default="standard")
    analysis_result = Column(Text, nullable=False, default="{}")        # JSON
    prediction_summary = Column(Text, nullable=False, default="{}")     # JSON
    scenario_result = Column(Text, nullable=True)                       # JSON
    overall_confidence = Column(Float, nullable=False, default=0.5)
    trend = Column(String(20), nullable=True)
    llm_provider = Column(String(30), nullable=True)
    llm_model = Column(String(100), nullable=True)
    token_count = Column(Integer, nullable=False, default=0)
    duration_ms = Column(Integer, nullable=False, default=0)
    is_shared = Column(Boolean, nullable=False, default=False)
    tags = Column(Text, nullable=False, default="[]")                   # JSON array
    created_at = Column(String, nullable=False, default=_now, index=True)
    updated_at = Column(String, nullable=False, default=_now)

    user = relationship("User", back_populates="analysis_records")
    favorites = relationship("Favorite", back_populates="analysis", cascade="all, delete-orphan")
    shared_reports = relationship("SharedReport", back_populates="analysis", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="analysis", cascade="all, delete-orphan")


# ─────────────── 收藏夹 ───────────────
class Favorite(Base):
    __tablename__ = "favorites"
    __table_args__ = (
        UniqueConstraint("user_id", "analysis_id", name="uq_favorites_user_analysis"),
    )

    id = Column(String, primary_key=True, default=_generate_id)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    analysis_id = Column(String, ForeignKey("analysis_history.id", ondelete="CASCADE"), nullable=False)
    notes = Column(Text, nullable=False, default="")
    folder = Column(String(100), nullable=False, default="default")
    created_at = Column(String, nullable=False, default=_now)

    user = relationship("User", back_populates="favorites")
    analysis = relationship("AnalysisHistory", back_populates="favorites")


# ─────────────── 共享报告 ───────────────
class SharedReport(Base):
    __tablename__ = "shared_reports"

    id = Column(String, primary_key=True, default=_generate_id)
    owner_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    analysis_id = Column(String, ForeignKey("analysis_history.id", ondelete="CASCADE"), nullable=False)
    report_type = Column(String(20), nullable=False, default="link")
    title = Column(String(500), nullable=False, default="")
    description = Column(Text, nullable=False, default="")
    share_token = Column(String, unique=True, nullable=False, index=True, default=_generate_id)
    is_public = Column(Boolean, nullable=False, default=True)
    workspace_id = Column(String, ForeignKey("workspaces.id"), nullable=True)
    password_hash = Column(String(255), nullable=True)
    expires_at = Column(String, nullable=True)
    view_count = Column(Integer, nullable=False, default=0)
    created_at = Column(String, nullable=False, default=_now)

    owner = relationship("User", back_populates="shared_reports")
    analysis = relationship("AnalysisHistory", back_populates="shared_reports")


# ─────────────── 团队工作区 ───────────────
class Workspace(Base):
    __tablename__ = "workspaces"

    id = Column(String, primary_key=True, default=_generate_id)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=False, default="")
    owner_id = Column(String, ForeignKey("users.id"), nullable=False)
    icon = Column(String(10), nullable=False, default="📁")
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(String, nullable=False, default=_now)
    updated_at = Column(String, nullable=False, default=_now)

    owner = relationship("User", back_populates="owned_workspaces")
    members = relationship("WorkspaceMember", back_populates="workspace", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="workspace")


class WorkspaceMember(Base):
    __tablename__ = "workspace_members"
    __table_args__ = (
        UniqueConstraint("workspace_id", "user_id", name="uq_workspace_member"),
    )

    id = Column(String, primary_key=True, default=_generate_id)
    workspace_id = Column(String, ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(20), nullable=False, default="viewer")  # owner / editor / viewer
    joined_at = Column(String, nullable=False, default=_now)

    workspace = relationship("Workspace", back_populates="members")
    user = relationship("User", back_populates="workspace_memberships")


# ─────────────── 评论 ───────────────
class Comment(Base):
    __tablename__ = "comments"

    id = Column(String, primary_key=True, default=_generate_id)
    analysis_id = Column(String, ForeignKey("analysis_history.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    workspace_id = Column(String, ForeignKey("workspaces.id"), nullable=True, index=True)
    parent_id = Column(String, ForeignKey("comments.id"), nullable=True)
    content = Column(Text, nullable=False)
    mentions = Column(Text, nullable=False, default="[]")  # JSON array of user IDs
    is_edited = Column(Boolean, nullable=False, default=False)
    created_at = Column(String, nullable=False, default=_now)
    updated_at = Column(String, nullable=False, default=_now)

    analysis = relationship("AnalysisHistory", back_populates="comments")
    user = relationship("User", back_populates="comments")
    workspace = relationship("Workspace", back_populates="comments")
    replies = relationship("Comment", backref="parent", remote_side=[id], cascade="all")
