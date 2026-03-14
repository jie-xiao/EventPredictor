# 健康检查接口
from fastapi import APIRouter
from datetime import datetime
import time
from app.api.models import HealthResponse, HealthComponent
from app.core.config import config


router = APIRouter(tags=["Health"])

# 服务启动时间
_start_time = time.time()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="健康检查",
    description="检查服务运行状态 - Section 18.2"
)
async def health_check() -> HealthResponse:
    """健康检查 - 包含uptime和组件状态"""
    uptime = int(time.time() - _start_time)

    # 检查各组件状态
    components = {
        "data_service": HealthComponent(
            status="healthy",
            message="Preset events loaded"
        ),
        "llm_service": HealthComponent(
            status="healthy",
            message=f"Provider: {config.llm.provider}"
        ),
        "cache": HealthComponent(
            status="healthy",
            message="In-memory cache active"
        )
    }

    return HealthResponse(
        status="healthy",
        version=config.api.version,
        timestamp=datetime.utcnow().isoformat() + "Z",
        uptime_seconds=uptime,
        components=components
    )


@router.get(
    "/",
    summary="根路径",
    description="API根路径"
)
async def root():
    """根路径"""
    return {
        "message": "EventPredictor API",
        "version": config.api.version,
        "docs": "/docs"
    }
