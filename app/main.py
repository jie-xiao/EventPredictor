# EventPredictor FastAPI应用入口
import os
import time
from collections import defaultdict
from typing import Dict, Tuple

# 解决HTTP代理导致的localhost请求503问题
# 确保NO_PROXY在所有HTTP请求之前设置
# 注意：setdefault不会覆盖已存在的值，所以这里用直接赋值确保设置
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
# P0阶段新增：缓存和模式匹配路由
from app.api.routes.cache import router as cache_router
from app.api.routes.pattern import router as pattern_router
from app.core.config import config


# ============ Rate Limiting Middleware - Section 16.3 ============
class RateLimitMiddleware(BaseHTTPMiddleware):
    """简单的内存限流中间件"""

    def __init__(self, app, requests_per_minute: int = 100):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, list] = defaultdict(list)

    def _get_client_ip(self, request: Request) -> str:
        """获取客户端IP"""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def _is_rate_limited(self, client_ip: str) -> bool:
        """检查是否超过限流"""
        now = time.time()
        minute_ago = now - 60

        # 清理过期记录
        self.requests[client_ip] = [
            t for t in self.requests[client_ip] if t > minute_ago
        ]

        # 检查数量
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            return True

        # 记录本次请求
        self.requests[client_ip].append(now)
        return False

    async def dispatch(self, request: Request, call_next):
        # 跳过健康检查和文档
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


# 创建FastAPI应用
app = FastAPI(
    title=config.api.title,
    version=config.api.version,
    description=config.api.description,
    docs_url="/docs",
    redoc_url="/redoc"
)

# 添加限流中间件 - Section 16.3
app.add_middleware(RateLimitMiddleware, requests_per_minute=100)

# 配置CORS - 从环境变量读取允许的源
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
# P0阶段新增：缓存和模式匹配路由
app.include_router(cache_router)
app.include_router(pattern_router)


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    print(f"EventPredictor v{config.api.version} starting...")
    print(f"LLM Provider: {config.llm.provider}")
    print(f"Model: {config.llm.model}")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    print("EventPredictor shutting down...")


# 导出app实例
__all__ = ["app"]
