# EventPredictor JWT 安全模块
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import config

# 密码哈希上下文
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=config.auth.bcrypt_rounds,
)

# JWT 配置
ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    """哈希密码"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: str, username: str, expires_delta: Optional[timedelta] = None) -> str:
    """创建 access token"""
    if expires_delta is None:
        expires_delta = timedelta(minutes=config.auth.access_token_expire_minutes)

    expire = datetime.now(timezone.utc) + expires_delta
    payload = {
        "sub": user_id,
        "username": username,
        "type": "access",
        "exp": expire,
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(payload, config.auth.secret_key, algorithm=ALGORITHM)


def create_refresh_token(user_id: str) -> str:
    """创建 refresh token"""
    expire = datetime.now(timezone.utc) + timedelta(days=config.auth.refresh_token_expire_days)
    payload = {
        "sub": user_id,
        "type": "refresh",
        "exp": expire,
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(payload, config.auth.secret_key, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    """解码并验证 token，返回 payload 或 None"""
    try:
        payload = jwt.decode(token, config.auth.secret_key, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
