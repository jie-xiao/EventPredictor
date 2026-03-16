# 模式匹配API
"""
P0阶段功能：历史模式匹配API
"""
from fastapi import APIRouter, HTTPException, status, Query
from typing import Optional, List
from pydantic import BaseModel, Field

from app.services.pattern_matcher_service import pattern_matcher


router = APIRouter(prefix="/api/v1/pattern", tags=["Pattern Matching"])


class EventInput(BaseModel):
    """事件输入"""
    title: str = Field(..., description="事件标题")
    description: str = Field(..., description="事件描述")
    category: str = Field(default="Other", description="事件类别")


class SimilarEventResult(BaseModel):
    """相似事件结果"""
    history_id: str
    event_id: Optional[str] = None
    title: str
    category: str
    similarity_score: float
    similarity_details: dict
    prediction: dict
    overall_confidence: Optional[float] = None
    created_at: Optional[str] = None


class PatternStatsResponse(BaseModel):
    """模式匹配统计响应"""
    total_predictions: int
    category_distribution: dict
    top_keywords: List[tuple]
    trend_distribution: dict
    pattern_index_size: int


class KeywordSearchRequest(BaseModel):
    """关键词搜索请求"""
    keywords: List[str] = Field(..., description="关键词列表")
    top_k: int = Field(default=10, ge=1, le=50, description="返回数量")


@router.post(
    "/find-similar",
    response_model=List[SimilarEventResult],
    summary="查找相似事件",
    description="查找与输入事件相似的历史事件"
)
async def find_similar_events(
    event: EventInput,
    top_k: int = Query(default=5, ge=1, le=20, description="返回最相似的K个结果"),
    min_similarity: float = Query(default=0.3, ge=0.0, le=1.0, description="最小相似度阈值")
):
    """查找相似的历史事件"""
    try:
        event_dict = event.model_dump()
        results = await pattern_matcher.find_similar_events(
            event_dict,
            top_k=top_k,
            min_similarity=min_similarity
        )
        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to find similar events: {str(e)}"
        )


@router.post(
    "/search-by-keywords",
    summary="按关键词搜索",
    description="基于关键词搜索历史模式"
)
async def search_by_keywords(request: KeywordSearchRequest):
    """按关键词搜索历史模式"""
    try:
        results = await pattern_matcher.find_similar_patterns_by_keywords(
            keywords=request.keywords,
            top_k=request.top_k
        )
        return {
            "keywords": request.keywords,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search by keywords: {str(e)}"
        )


@router.get(
    "/statistics",
    response_model=PatternStatsResponse,
    summary="获取模式匹配统计",
    description="获取历史模式匹配的统计信息"
)
async def get_pattern_statistics():
    """获取模式匹配统计信息"""
    try:
        stats = await pattern_matcher.get_pattern_statistics()
        return PatternStatsResponse(
            total_predictions=stats.get("total_predictions", 0),
            category_distribution=stats.get("category_distribution", {}),
            top_keywords=stats.get("top_keywords", []),
            trend_distribution=stats.get("trend_distribution", {}),
            pattern_index_size=stats.get("pattern_index_size", 0)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get pattern statistics: {str(e)}"
        )


@router.get(
    "/categories",
    summary="获取类别分布",
    description="获取历史事件的类别分布"
)
async def get_category_distribution():
    """获取类别分布"""
    try:
        stats = await pattern_matcher.get_pattern_statistics()
        return {
            "distribution": stats.get("category_distribution", {}),
            "total": stats.get("total_predictions", 0)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get category distribution: {str(e)}"
        )


@router.get(
    "/trends",
    summary="获取趋势分布",
    description="获取历史预测的趋势分布"
)
async def get_trend_distribution():
    """获取趋势分布"""
    try:
        stats = await pattern_matcher.get_pattern_statistics()
        return {
            "distribution": stats.get("trend_distribution", {}),
            "total": stats.get("total_predictions", 0)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get trend distribution: {str(e)}"
        )


@router.get(
    "/keywords",
    summary="获取高频关键词",
    description="获取历史事件中的高频关键词"
)
async def get_top_keywords(
    limit: int = Query(default=20, ge=1, le=100, description="返回关键词数量")
):
    """获取高频关键词"""
    try:
        stats = await pattern_matcher.get_pattern_statistics()
        top_keywords = stats.get("top_keywords", [])[:limit]
        return {
            "keywords": [{"keyword": kw, "frequency": freq} for kw, freq in top_keywords],
            "count": len(top_keywords)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get top keywords: {str(e)}"
        )
