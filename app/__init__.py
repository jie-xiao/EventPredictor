# EventPredictor - 全球局势推演决策系统

"""
EventPredictor - 全球局势推演决策系统

基于多智能体协作的事件分析和未来走势预测系统
"""

__version__ = "1.0.0"
__author__ = "EventPredictor Team"

from app.main import app
from app.api.models import Event, Prediction, PredictRequest, PredictResponse

__all__ = [
    "app",
    "Event",
    "Prediction", 
    "PredictRequest",
    "PredictResponse"
]
