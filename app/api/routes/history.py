# 预测历史记录API
from fastapi import APIRouter, HTTPException, status, Query
from typing import Optional
from pydantic import BaseModel, Field
from app.services.history_service import history_service


router = APIRouter(prefix="/api/v1/history", tags=["Prediction History"])


class SavePredictionRequest(BaseModel):
    """保存预测请求"""
    event_id: str = Field(..., description="事件ID")
    event_title: str = Field(..., description="事件标题")
    event_description: str = Field(..., description="事件描述")
    prediction_result: dict = Field(..., description="预测分析结果")
    scenario_result: Optional[dict] = Field(default=None, description="情景推演结果")


class UpdatePredictionRequest(BaseModel):
    """更新预测请求"""
    scenario: Optional[dict] = Field(default=None, description="情景推演结果")


@router.post(
    "/save",
    summary="保存预测结果",
    description="将预测分析结果保存到历史记录"
)
async def save_prediction(request: SavePredictionRequest):
    """保存预测结果"""
    try:
        record = await history_service.save_prediction(
            event_id=request.event_id,
            event_title=request.event_title,
            event_description=request.event_description,
            prediction_result=request.prediction_result,
            scenario_result=request.scenario_result
        )
        return {
            "success": True,
            "record": record
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save prediction: {str(e)}"
        )


@router.get(
    "/list",
    summary="获取预测历史列表",
    description="分页获取预测历史记录"
)
async def list_predictions(
    page: int = Query(default=1, ge=1, description="页码"),
    page_size: int = Query(default=20, ge=1, le=100, description="每页数量"),
    category: Optional[str] = Query(default=None, description="筛选类别"),
    start_date: Optional[str] = Query(default=None, description="开始日期 (ISO格式)"),
    end_date: Optional[str] = Query(default=None, description="结束日期 (ISO格式)")
):
    """获取预测历史列表"""
    try:
        result = await history_service.list_predictions(
            page=page,
            page_size=page_size,
            category=category,
            start_date=start_date,
            end_date=end_date
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list predictions: {str(e)}"
        )


@router.get(
    "/{record_id}",
    summary="获取单条预测记录",
    description="根据ID获取预测记录详情"
)
async def get_prediction(record_id: str):
    """获取单条预测记录"""
    record = await history_service.get_prediction(record_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prediction {record_id} not found"
        )
    return record


@router.get(
    "/event/{event_id}",
    summary="获取事件的所有预测",
    description="获取特定事件的所有预测记录"
)
async def get_predictions_by_event(event_id: str):
    """获取事件的所有预测记录"""
    records = await history_service.get_predictions_by_event(event_id)
    return {
        "event_id": event_id,
        "predictions": records,
        "count": len(records)
    }


@router.put(
    "/{record_id}",
    summary="更新预测记录",
    description="更新预测记录（如添加新的情景推演）"
)
async def update_prediction(record_id: str, request: UpdatePredictionRequest):
    """更新预测记录"""
    record = await history_service.update_prediction(
        record_id=record_id,
        updates=request.dict(exclude_unset=True)
    )
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prediction {record_id} not found"
        )
    return record


@router.delete(
    "/{record_id}",
    summary="删除预测记录",
    description="删除指定的预测记录"
)
async def delete_prediction(record_id: str):
    """删除预测记录"""
    success = await history_service.delete_prediction(record_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prediction {record_id} not found"
        )
    return {"success": True, "message": f"Prediction {record_id} deleted"}


@router.get(
    "/statistics/summary",
    summary="获取统计信息",
    description="获取预测历史统计摘要"
)
async def get_statistics():
    """获取统计信息"""
    return await history_service.get_statistics()


@router.get(
    "/export/{format}",
    summary="导出历史记录",
    description="导出预测历史记录 (json/csv)"
)
async def export_history(format: str = "json"):
    """导出历史记录"""
    if format not in ["json", "csv"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Format must be 'json' or 'csv'"
        )

    content = await history_service.export_history(format)
    media_type = "application/json" if format == "json" else "text/csv"

    from fastapi.responses import Response
    return Response(
        content=content,
        media_type=media_type,
        headers={
            "Content-Disposition": f"attachment; filename=prediction_history.{format}"
        }
    )
