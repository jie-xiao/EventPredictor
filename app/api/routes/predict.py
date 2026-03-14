# 预测接口
from fastapi import APIRouter, HTTPException, status
from app.api.models import PredictRequest, PredictResponse, ErrorResponse
from app.services.prediction_service import prediction_service


router = APIRouter(prefix="/api/v1", tags=["Prediction"])


@router.post(
    "/predict", 
    response_model=PredictResponse,
    summary="提交事件进行预测",
    description="接收一个事件，返回基于多Agent分析的预测结果"
)
async def predict(request: PredictRequest) -> PredictResponse:
    """预测接口"""
    try:
        result = await prediction_service.predict(request)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/predictions",
    response_model=list,
    summary="获取预测列表"
)
async def list_predictions(page: int = 1, page_size: int = 20):
    """获取预测列表"""
    predictions = await prediction_service.list_predictions(page, page_size)
    return predictions


@router.get(
    "/predictions/{prediction_id}",
    response_model=PredictResponse,
    summary="获取单个预测结果"
)
async def get_prediction(prediction_id: str):
    """获取单个预测"""
    prediction = await prediction_service.get_prediction(prediction_id)
    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prediction {prediction_id} not found"
        )
    return PredictResponse.from_prediction(prediction)
