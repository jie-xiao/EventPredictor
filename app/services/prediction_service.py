# 预测服务
# P0阶段功能：集成历史模式匹配 + 响应缓存
import uuid
import json
import os
from typing import Optional, Dict, Any, List
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
from app.services.response_cache_service import response_cache
from app.services.pattern_matcher_service import pattern_matcher
from app.services.history_service import history_service

# 数据持久化目录
DATA_DIR = Path(os.getenv("DATA_DIR", "data"))
EVENTS_FILE = DATA_DIR / "events.json"
PREDICTIONS_FILE = DATA_DIR / "predictions.json"


class PredictionService:
    """预测服务 - 业务逻辑层（P0阶段：集成缓存和模式匹配）"""

    def __init__(self):
        self.pipeline = AgentPipeline()
        self._events_store: dict = {}
        self._predictions_store: dict = {}
        # P0阶段：缓存和模式匹配服务
        self.cache = response_cache
        self.pattern_matcher = pattern_matcher
        self.history_service = history_service
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
    
    async def predict(
        self,
        request: PredictRequest,
        use_cache: bool = True,
        find_similar: bool = True
    ) -> PredictResponse:
        """
        执行预测（P0阶段：集成缓存和模式匹配）

        Args:
            request: 预测请求
            use_cache: 是否使用缓存（默认True）
            find_similar: 是否查找相似历史事件（默认True）

        Returns:
            预测响应
        """
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

        # P0阶段：尝试从缓存获取
        if use_cache:
            event_dict = event.model_dump()
            cached_result = await self.cache.get(event_dict, "prediction")

            if cached_result is not None:
                # 缓存命中，直接返回
                cache_hit_type = cached_result.pop("_cache_hit_type", "exact")
                response = PredictResponse(**cached_result)
                # 标记为缓存命中
                response.reasoning = f"[缓存命中: {cache_hit_type}] " + response.reasoning
                return response

        # P0阶段：查找相似历史事件
        similar_events = []
        if find_similar:
            event_dict = event.model_dump()
            similar_events = await self.pattern_matcher.find_similar_events(
                event_dict,
                top_k=3,
                min_similarity=0.4
            )

        # 运行Agent Pipeline
        prediction, analysis = self.pipeline.run_with_analysis(event)

        # 存储预测结果
        self._predictions_store[prediction.id] = prediction

        # 生成响应
        response = PredictResponse.from_prediction(prediction, analysis)

        # P0阶段：如果有相似事件，添加到响应中
        if similar_events:
            response.related_events = [
                {
                    "title": s.get("title"),
                    "similarity": s.get("similarity_score"),
                    "trend": s.get("prediction", {}).get("trend"),
                    "confidence": s.get("prediction", {}).get("confidence")
                }
                for s in similar_events
            ]

        # P0阶段：缓存结果
        if use_cache:
            event_dict = event.model_dump()
            response_dict = response.model_dump()
            await self.cache.set(event_dict, response_dict, "prediction")

        # P0阶段：保存到历史记录并学习模式
        prediction_record = {
            "id": prediction.id,
            "event_id": event.id,
            "event_title": event.title,
            "event_description": event.description,
            "category": event.category,
            "prediction": {
                "trend": prediction.trend.value,
                "confidence": prediction.confidence,
                "summary": response.reasoning[:200]
            },
            "overall_confidence": prediction.confidence
        }

        # 保存到历史服务
        await self.history_service.save_prediction(
            event_id=event.id,
            event_title=event.title,
            event_description=event.description,
            prediction_result={"prediction": prediction_record["prediction"]},
            scenario_result=None
        )

        # 学习新模式
        await self.pattern_matcher.learn_from_new_prediction(prediction_record)

        # 持久化到磁盘
        self._save_to_disk()

        return response
    
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

    # ============ P0阶段新增方法：缓存管理 ============

    async def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        return await self.cache.get_stats()

    async def clear_cache(self, expired_only: bool = False) -> Dict[str, str]:
        """清空缓存"""
        await self.cache.clear(expired_only=expired_only)
        return {"status": "success", "message": f"缓存已{'清除过期条目' if expired_only else '全部清空'}"}

    async def get_similar_events(
        self,
        event: Dict[str, Any],
        top_k: int = 5,
        min_similarity: float = 0.3
    ) -> List[Dict[str, Any]]:
        """
        查找相似的历史事件

        Args:
            event: 事件信息
            top_k: 返回最相似的K个结果
            min_similarity: 最小相似度阈值

        Returns:
            相似事件列表
        """
        return await self.pattern_matcher.find_similar_events(
            event,
            top_k=top_k,
            min_similarity=min_similarity
        )

    async def get_pattern_stats(self) -> Dict[str, Any]:
        """获取模式匹配统计信息"""
        return await self.pattern_matcher.get_pattern_statistics()

    async def predict_with_similarity(
        self,
        request: PredictRequest,
        similarity_threshold: float = 0.7
    ) -> Dict[str, Any]:
        """
        带相似度检查的预测

        如果存在高相似度的历史事件，直接返回历史预测结果，
        否则执行新的预测。

        Args:
            request: 预测请求
            similarity_threshold: 相似度阈值，超过此值直接复用

        Returns:
            包含预测结果和相似事件信息的字典
        """
        # 先查找相似事件
        event_dict = {
            "title": request.title,
            "description": request.description,
            "category": request.category
        }

        similar_events = await self.pattern_matcher.find_similar_events(
            event_dict,
            top_k=3,
            min_similarity=similarity_threshold
        )

        # 如果有高相似度事件，复用结果
        if similar_events and similar_events[0].get("similarity_score", 0) >= similarity_threshold:
            best_match = similar_events[0]
            return {
                "prediction": best_match.get("prediction"),
                "source": "historical_match",
                "matched_event": {
                    "title": best_match.get("title"),
                    "similarity": best_match.get("similarity_score"),
                    "history_id": best_match.get("history_id")
                },
                "confidence_adjustment": f"基于历史相似事件（相似度: {best_match.get('similarity_score'):.2%}）"
            }

        # 执行新预测
        response = await self.predict(request)

        return {
            "prediction": response.model_dump(),
            "source": "new_prediction",
            "similar_events": [
                {
                    "title": s.get("title"),
                    "similarity": s.get("similarity_score"),
                    "trend": s.get("prediction", {}).get("trend")
                }
                for s in similar_events
            ] if similar_events else [],
            "confidence_adjustment": "基于新分析"
        }

    async def batch_predict_with_cache(
        self,
        requests: List[PredictRequest],
        use_cache: bool = True
    ) -> List[Dict[str, Any]]:
        """
        批量预测（带缓存支持）

        Args:
            requests: 预测请求列表
            use_cache: 是否使用缓存

        Returns:
            预测结果列表
        """
        results = []

        for request in requests:
            try:
                response = await self.predict(request, use_cache=use_cache)
                results.append({
                    "success": True,
                    "title": request.title,
                    "prediction": response.model_dump()
                })
            except Exception as e:
                results.append({
                    "success": False,
                    "title": request.title,
                    "error": str(e)
                })

        return results


# 全局服务实例
prediction_service = PredictionService()
