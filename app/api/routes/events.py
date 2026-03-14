# 事件接口
from fastapi import APIRouter, HTTPException, status, Query
from typing import Optional
from app.api.models import (
    EventListResponse, Event, ErrorResponse, ErrorDetail, ErrorCodes
)
from app.services.prediction_service import prediction_service
from app.services.worldmonitor_service import worldmonitor_service
from app.services.data_service import data_service


router = APIRouter(prefix="/api/v1", tags=["Events"])


def raise_error(code: int, message: str, detail: str = None, status_code: int = 400):
    """标准化错误响应 - Section 15"""
    raise HTTPException(
        status_code=status_code,
        detail=ErrorDetail(code=code, message=message, detail=detail).model_dump()
    )


@router.get(
    "/events",
    response_model=EventListResponse,
    summary="获取事件列表",
    description="分页获取历史事件列表"
)
async def list_events(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量")
):
    """获取事件列表"""
    events = await prediction_service.list_events(page, page_size)
    total = len(prediction_service._events_store)

    return EventListResponse(
        events=events,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get(
    "/events/{event_id}",
    response_model=Event,
    summary="获取单个事件"
)
async def get_event(event_id: str):
    """获取单个事件"""
    event = await prediction_service.get_event(event_id)
    if not event:
        raise_error(
            code=ErrorCodes.EVENT_NOT_FOUND,
            message="Event not found",
            detail=f"Event {event_id} does not exist",
            status_code=404
        )
    return event


@router.get(
    "/worldmonitor/events",
    summary="从WorldMonitor获取事件",
    description="从WorldMonitor获取实时事件数据"
)
async def get_worldmonitor_events(
    category: Optional[str] = Query(None, description="事件类别"),
    limit: int = Query(50, ge=1, le=200, description="返回数量"),
    time_range: str = Query("24h", description="时间范围 (1h, 6h, 24h, 48h, 7d, all)")
):
    """从WorldMonitor获取实时事件"""
    try:
        events_data = await worldmonitor_service.fetch_events(
            category=category,
            limit=limit,
            time_range=time_range
        )
        return events_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch WorldMonitor events: {str(e)}"
        )


@router.get(
    "/worldmonitor/predictions",
    summary="从WorldMonitor获取预测市场",
    description="从WorldMonitor获取Polymarket预测市场数据"
)
async def get_worldmonitor_predictions(
    category: Optional[str] = Query(None, description="预测类别"),
    limit: int = Query(20, ge=1, le=100, description="返回数量")
):
    """从WorldMonitor获取预测市场数据"""
    try:
        predictions = await worldmonitor_service.fetch_polymarket_events(
            category=category,
            limit=limit
        )
        return {"predictions": predictions}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch predictions: {str(e)}"
        )


@router.get(
    "/worldmonitor/conflicts",
    summary="从WorldMonitor获取冲突事件",
    description="从WorldMonitor获取冲突事件数据"
)
async def get_worldmonitor_conflicts(
    region: Optional[str] = Query(None, description="地区"),
    limit: int = Query(50, ge=1, le=200, description="返回数量")
):
    """从WorldMonitor获取冲突事件"""
    try:
        events = await worldmonitor_service.fetch_conflict_events(
            region=region,
            limit=limit
        )
        return {"events": events}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch conflicts: {str(e)}"
        )


@router.get(
    "/worldmonitor/intelligence",
    summary="从WorldMonitor获取情报信号",
    description="从WorldMonitor获取情报信号数据"
)
async def get_worldmonitor_intelligence(
    limit: int = Query(50, ge=1, le=200, description="返回数量")
):
    """从WorldMonitor获取情报信号"""
    try:
        signals = await worldmonitor_service.fetch_intelligence_signals(limit=limit)
        return {"signals": signals}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch intelligence: {str(e)}"
        )


@router.get(
    "/worldmonitor/summary",
    summary="获取WorldMonitor摘要",
    description="获取WorldMonitor事件摘要"
)
async def get_worldmonitor_summary():
    """获取WorldMonitor事件摘要"""
    try:
        summary = await worldmonitor_service.get_event_summary()
        return summary
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch summary: {str(e)}"
        )


@router.get(
    "/worldmonitor/health",
    summary="检查WorldMonitor连接",
    description="检查WorldMonitor API是否可连接"
)
async def check_worldmonitor_health():
    """检查WorldMonitor API连接"""
    connected = await worldmonitor_service.check_connection()
    return {
        "connected": connected,
        "url": worldmonitor_service.base_url
    }


@router.post(
    "/worldmonitor/import",
    summary="从WorldMonitor导入并预测",
    description="从WorldMonitor获取事件并进行预测"
)
async def import_and_predict(
    source: str = Query("news", description="事件来源 (news, predictions, conflicts, intelligence)"),
    limit: int = Query(5, ge=1, le=20, description="处理的事件数量")
):
    """从WorldMonitor导入事件并进行预测"""
    try:
        results = await prediction_service.predict_from_worldmonitor(
            event_source=source,
            limit=limit
        )
        return {
            "imported": len(results),
            "results": results
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to import and predict: {str(e)}"
        )


# ============ 内置事件数据接口 ============

@router.get(
    "/data/events",
    response_model=EventListResponse,
    summary="获取内置事件列表",
    description="从内置预置数据获取事件列表"
)
async def get_preset_events(
    category: Optional[str] = Query(None, description="事件类别过滤"),
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    time_range: str = Query("24h", description="时间范围 (1h, 6h, 24h, 48h, 7d, 30d, all)")
):
    """获取内置事件列表"""
    events = await data_service.get_events(
        category=category,
        limit=limit,
        time_range=time_range
    )
    
    return EventListResponse(
        events=events,
        total=len(events),
        page=1,
        page_size=limit
    )


@router.get(
    "/data/events/{event_id}",
    response_model=Event,
    summary="获取单个内置事件"
)
async def get_preset_event(event_id: str):
    """获取单个内置事件"""
    event = await data_service.get_event_by_id(event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event {event_id} not found"
        )
    return event


@router.get(
    "/data/categories",
    summary="获取事件类别列表",
    description="获取所有可用的内置事件类别"
)
async def get_event_categories():
    """获取事件类别列表"""
    return {
        "categories": data_service.get_categories(),
        "total": data_service.get_event_count()
    }


@router.post(
    "/data/refresh",
    summary="刷新内置数据",
    description="重新加载内置事件数据"
)
async def refresh_preset_data():
    """刷新内置数据"""
    success = await data_service.refresh_data()
    if success:
        return {
            "status": "success",
            "message": f"Reloaded {data_service.get_event_count()} events"
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to refresh data"
        )
