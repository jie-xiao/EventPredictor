# EventPredictor FastAPI应用入口
import os
import time
from collections import defaultdict
from contextlib import asynccontextmanager
from typing import Dict, Tuple

# 解决HTTP代理导致的localhost请求503问题
_no_proxy_values = "localhost,127.0.0.1,0.0.0.0,::1,local,.local"
os.environ["NO_PROXY"] = _no_proxy_values
os.environ["no_proxy"] = _no_proxy_values

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from app.api.routes import predict, events, health
from app.api.routes.multi_agent import router as multi_agent_router
from app.api.routes.debate import router as debate_router
from app.api.routes.history import router as history_router
from app.api.routes.reaction_chain import router as reaction_chain_router
from app.api.routes.multi_agent_coordination import router as multi_agent_coordination_router
from app.api.routes.cache import router as cache_router
from app.api.routes.pattern import router as pattern_router
from app.api.routes.sandbox import router as sandbox_router
from app.api.routes.report import router as report_router
from app.api.routes.knowledge_graph import router as knowledge_graph_router
from app.api.routes.event_monitor import router as event_monitor_router
from app.api.routes.auth import router as auth_router
from app.api.routes.users import router as users_router
from app.api.routes.advanced_analysis import router as advanced_analysis_router
from app.core.config import config


# ============ Rate Limiting Middleware ============
class RateLimitMiddleware(BaseHTTPMiddleware):
    """简单的内存限流中间件"""

    def __init__(self, app, requests_per_minute: int = 100):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, list] = defaultdict(list)

    def _get_client_ip(self, request: Request) -> str:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def _is_rate_limited(self, client_ip: str) -> bool:
        now = time.time()
        minute_ago = now - 60
        self.requests[client_ip] = [
            t for t in self.requests[client_ip] if t > minute_ago
        ]
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            return True
        self.requests[client_ip].append(now)
        return False

    async def dispatch(self, request: Request, call_next):
        if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        client_ip = self._get_client_ip(request)
        if self._is_rate_limited(client_ip):
            return Response(
                content='{"error": {"code": 1006, "message": "Rate limit exceeded", "detail": "Too many requests"}}',
                status_code=429,
                media_type="application/json"
            )
        return await call_next(request)


# Lifespan 上下文管理器
@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # Startup
    print(f"EventPredictor v{config.api.version} starting...")
    print(f"LLM Provider: {config.llm.provider}")
    print(f"Model: {config.llm.model}")

    # Initialize database
    try:
        from app.db.database import init_db, cleanup_db
        await init_db()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Database initialization warning: {e}")
        print("Continuing with file-based storage fallback")

    yield

    # Shutdown
    try:
        from app.db.database import cleanup_db
        await cleanup_db()
    except Exception:
        pass
    print("EventPredictor shutting down...")


# 创建FastAPI应用
app = FastAPI(
    title=config.api.title,
    version=config.api.version,
    description=config.api.description,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 添加限流中间件
app.add_middleware(RateLimitMiddleware, requests_per_minute=100)

# 配置CORS
_cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(health.router)
app.include_router(predict.router)
app.include_router(events.router)
app.include_router(multi_agent_router)
app.include_router(debate_router)
app.include_router(history_router)
app.include_router(reaction_chain_router)
app.include_router(multi_agent_coordination_router)
app.include_router(cache_router)
app.include_router(pattern_router)
app.include_router(sandbox_router)
app.include_router(report_router)
app.include_router(knowledge_graph_router)
app.include_router(event_monitor_router)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(advanced_analysis_router)


# 导出app实例
__all__ = ["app"]
