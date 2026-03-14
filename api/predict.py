"""
预测API模块
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from agents.event_agent import EventAgent

router = APIRouter()

# 初始化Agent
event_agent = EventAgent()


class PredictRequest(BaseModel):
    """预测请求模型"""
    event_type: str
    context: Dict[str, Any]
    history_data: Optional[List[Dict[str, Any]]] = None


class PredictResponse(BaseModel):
    """预测响应模型"""
    prediction: str
    confidence: float
    factors: List[str]
    recommendation: Optional[str] = None


@router.post("/predict", response_model=PredictResponse)
async def predict_event(request: PredictRequest):
    """
    事件预测 endpoint
    
    Args:
        request: 预测请求，包含事件类型、上下文和历史数据
        
    Returns:
        预测结果
    """
    try:
        result = await event_agent.predict(
            event_type=request.event_type,
            context=request.context,
            history_data=request.history_data
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/predict/{event_type}")
async def get_prediction_example(event_type: str):
    """获取预测示例"""
    return {
        "event_type": event_type,
        "example_context": {
            "location": "北京",
            "time": "2024-01-01",
            "category": "技术会议"
        }
    }
