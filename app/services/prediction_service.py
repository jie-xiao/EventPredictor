# 预测服务
import uuid
import json
import os
from typing import Optional
from datetime import datetime
from pathlib import Path
from app.agents.pipeline import AgentPipeline
from app.api.models import (
    Event,
    Prediction,
    PredictRequest,
    PredictResponse,
    TrendDirection
)
from app.services.worldmonitor_service import worldmonitor_service

# 数据持久化目录
DATA_DIR = Path(os.getenv("DATA_DIR", "data"))
EVENTS_FILE = DATA_DIR / "events.json"
PREDICTIONS_FILE = DATA_DIR / "predictions.json"


class PredictionService:
    """预测服务 - 业务逻辑层"""

    def __init__(self):
        self.pipeline = AgentPipeline()
        self._events_store: dict = {}
        self._predictions_store: dict = {}
        # 加载持久化数据
        self._load_from_disk()

    def _load_from_disk(self):
        """从磁盘加载持久化数据"""
        try:
            # 确保目录存在
            DATA_DIR.mkdir(parents=True, exist_ok=True)

            # 加载事件
            if EVENTS_FILE.exists():
                with open(EVENTS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._events_store = {k: Event(**v) for k, v in data.items()}

            # 加载预测
            if PREDICTIONS_FILE.exists():
                with open(PREDICTIONS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._predictions_store = {k: Prediction(**v) for k, v in data.items()}
        except Exception:
            # 加载失败时使用空存储
            self._events_store = {}
            self._predictions_store = {}

    def _save_to_disk(self):
        """保存数据到磁盘"""
        try:
            # 确保目录存在
            DATA_DIR.mkdir(parents=True, exist_ok=True)

            # 保存事件
            events_data = {k: v.model_dump() for k, v in self._events_store.items()}
            with open(EVENTS_FILE, 'w', encoding='utf-8') as f:
                json.dump(events_data, f, ensure_ascii=False, indent=2, default=str)

            # 保存预测
            predictions_data = {k: v.model_dump() for k, v in self._predictions_store.items()}
            with open(PREDICTIONS_FILE, 'w', encoding='utf-8') as f:
                json.dump(predictions_data, f, ensure_ascii=False, indent=2, default=str)
        except Exception:
            pass  # 保存失败时静默处理，不影响主流程
    
    async def predict(self, request: PredictRequest) -> PredictResponse:
        """执行预测"""
        # 创建事件
        event = Event(
            id=f"evt-{uuid.uuid4().hex[:8]}",
            title=request.title,
            description=request.description,
            source=request.source,
            timestamp=request.timestamp or datetime.utcnow().isoformat() + "Z",
            category=request.category,
            importance=request.importance
        )
        
        # 存储事件
        self._events_store[event.id] = event

        # 运行Agent Pipeline
        prediction, analysis = self.pipeline.run_with_analysis(event)

        # 存储预测结果
        self._predictions_store[prediction.id] = prediction

        # 持久化到磁盘
        self._save_to_disk()

        return PredictResponse.from_prediction(prediction, analysis)
    
    async def predict_from_worldmonitor(
        self,
        event_source: str = "news",
        limit: int = 5
    ) -> list:
        """
        从WorldMonitor获取事件并进行预测
        
        Args:
            event_source: 事件来源 (news, predictions, conflicts, intelligence)
            limit: 处理的事件数量
        
        Returns:
            预测结果列表
        """
        results = []
        
        # 获取事件数据
        if event_source == "news":
            events_data = await worldmonitor_service.fetch_events(limit=limit)
            events = events_data.get("events", [])
        elif event_source == "predictions":
            events = await worldmonitor_service.fetch_polymarket_events(limit=limit)
        elif event_source == "conflicts":
            events = await worldmonitor_service.fetch_conflict_events(limit=limit)
        elif event_source == "intelligence":
            events = await worldmonitor_service.fetch_intelligence_signals(limit=limit)
        else:
            events = []
        
        # 对每个事件进行预测
        for event_data in events:
            try:
                # 转换WorldMonitor事件为Event模型
                title = event_data.get("title", event_data.get("question", ""))
                description = event_data.get("description", event_data.get("summary", ""))
                
                if not title:
                    continue
                
                # 创建事件
                event = Event(
                    id=f"evt-wm-{uuid.uuid4().hex[:8]}",
                    title=title,
                    description=description,
                    source=f"WorldMonitor-{event_source}",
                    timestamp=event_data.get("timestamp", datetime.utcnow().isoformat() + "Z"),
                    category=event_data.get("category", "Geopolitical"),
                    importance=event_data.get("importance", 3)
                )
                
                # 存储事件
                self._events_store[event.id] = event

                # 运行预测
                prediction, analysis = self.pipeline.run_with_analysis(event)

                # 存储预测
                self._predictions_store[prediction.id] = prediction

                results.append({
                    "event": event,
                    "prediction": PredictResponse.from_prediction(prediction, analysis)
                })
            except Exception as e:
                continue

        # 持久化到磁盘
        self._save_to_disk()

        return results
    
    async def get_event(self, event_id: str) -> Optional[Event]:
        """获取事件"""
        return self._events_store.get(event_id)
    
    async def get_prediction(self, prediction_id: str) -> Optional[Prediction]:
        """获取预测结果"""
        return self._predictions_store.get(prediction_id)
    
    async def list_events(self, page: int = 1, page_size: int = 20) -> list:
        """列出事件"""
        events = list(self._events_store.values())
        start = (page - 1) * page_size
        end = start + page_size
        return events[start:end]
    
    async def list_predictions(self, page: int = 1, page_size: int = 20) -> list:
        """列出预测结果"""
        predictions = list(self._predictions_store.values())
        start = (page - 1) * page_size
        end = start + page_size
        return predictions[start:end]


# 全局服务实例
prediction_service = PredictionService()
