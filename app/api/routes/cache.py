# 缓存管理API
"""
P0阶段功能：响应缓存管理API
"""
from fastapi import APIRouter, HTTPException, status, Query
from typing import Optional
from pydantic import BaseModel, Field

from app.services.response_cache_service import response_cache


router = APIRouter(prefix="/api/v1/cache", tags=["Cache Management"])


class CacheStatsResponse(BaseModel):
    """缓存统计响应"""
    total_requests: int
    hits: int
    misses: int
    hit_rate: float
    cache_size: int
    evictions: int
    max_size: int
    ttl_seconds: int


class ClearCacheRequest(BaseModel):
    """清空缓存请求"""
    expired_only: bool = Field(default=False, description="是否只清除过期缓存")


@router.get(
    "/stats",
    response_model=CacheStatsResponse,
    summary="获取缓存统计信息",
    description="获取缓存的命中率、大小等统计信息"
)
async def get_cache_stats():
    """获取缓存统计信息"""
    try:
        stats = await response_cache.get_stats()
        return CacheStatsResponse(**stats)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get cache stats: {str(e)}"
        )


@router.post(
    "/clear",
    summary="清空缓存",
    description="清空所有缓存或只清除过期缓存"
)
async def clear_cache(request: ClearCacheRequest = ClearCacheRequest()):
    """清空缓存"""
    try:
        await response_cache.clear(expired_only=request.expired_only)
        return {
            "success": True,
            "message": f"缓存已{'清除过期条目' if request.expired_only else '全部清空'}"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear cache: {str(e)}"
        )


@router.get(
    "/keys",
    summary="获取缓存键列表",
    description="获取所有缓存键或匹配特定模式的键"
)
async def get_cache_keys(
    pattern: Optional[str] = Query(default=None, description="键模式匹配（支持通配符）")
):
    """获取缓存键列表"""
    try:
        keys = await response_cache.get_cache_keys(pattern=pattern)
        return {
            "keys": keys,
            "count": len(keys),
            "pattern": pattern
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get cache keys: {str(e)}"
        )


@router.get(
    "/entry/{cache_key:path}",
    summary="获取缓存条目详情",
    description="获取单个缓存条目的详细信息"
)
async def get_cache_entry(cache_key: str):
    """获取单个缓存条目"""
    try:
        entry = await response_cache.get_cache_entry(cache_key)
        if not entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cache entry '{cache_key}' not found or expired"
            )
        return entry
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get cache entry: {str(e)}"
        )


@router.delete(
    "/entry/{cache_key:path}",
    summary="删除缓存条目",
    description="删除指定的缓存条目"
)
async def delete_cache_entry(cache_key: str):
    """删除缓存条目"""
    # 注意：当前实现不直接支持按键删除，这里是个简化版本
    return {
        "success": True,
        "message": f"Cache entry deletion requested for '{cache_key}'",
        "note": "Use /clear endpoint to actually clear cache"
    }
