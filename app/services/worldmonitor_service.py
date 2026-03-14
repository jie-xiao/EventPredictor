# WorldMonitor数据接入服务 - 集成WorldMonitor API
import os
import httpx
import asyncio
import json
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from app.core.config import config

# 解决HTTP代理导致的localhost请求503问题
_no_proxy_hosts = [
    "localhost", "127.0.0.1", "0.0.0.0", "::1", "local", ".local",
    "api.minimax.chat", "api.anthropic.com", "api.openai.com",
    "gamma-api.polymarket.com", "clob.polymarket.com"
]
_no_proxy_value = ",".join(_no_proxy_hosts)
os.environ["NO_PROXY"] = _no_proxy_value
os.environ["no_proxy"] = _no_proxy_value
os.environ.pop("HTTP_PROXY", None)
os.environ.pop("HTTPS_PROXY", None)
os.environ.pop("http_proxy", None)
os.environ.pop("https_proxy", None)


class WorldMonitorService:
    """WorldMonitor数据接入服务 - 连接到WorldMonitor本地API获取事件数据"""

    def __init__(self):
        # WorldMonitor runs on port 3000 by default
        self.base_url = config.worldmonitor.local_api_url if hasattr(config, 'worldmonitor') and config.worldmonitor.local_api_url else "http://localhost:3000"
        self.timeout = 15.0
        self._connected = None

    def _get_client(self) -> httpx.AsyncClient:
        """获取HTTP客户端"""
        is_local = "localhost" in self.base_url or "127.0.0.1" in self.base_url
        return httpx.AsyncClient(
            timeout=self.timeout,
            follow_redirects=True,
            trust_env=not is_local,
            proxy=None
        )

    async def check_connection(self) -> bool:
        """检查WorldMonitor API连接"""
        try:
            async with self._get_client() as client:
                response = await client.get(f"{self.base_url}/")
                self._connected = response.status_code == 200
                return self._connected
        except Exception as e:
            print(f"WorldMonitor connection failed: {e}")
            self._connected = False
            return False

    # ============ Conflict Events (ACLED/UCDP) ============

    async def fetch_conflict_events(
        self,
        country: Optional[str] = None,
        days_back: int = 30,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """获取冲突事件 - ACLED数据"""
        try:
            async with self._get_client() as client:
                now = int(datetime.now().timestamp() * 1000)
                start = int((datetime.now() - timedelta(days=days_back)).timestamp() * 1000)

                payload = {
                    "timeRange": {"start": start, "end": now},
                    "pagination": {"pageSize": limit, "cursor": ""}
                }
                if country:
                    payload["country"] = country

                response = await client.post(
                    f"{self.base_url}/api/conflict/v1/list-acled-events",
                    json=payload
                )

                if response.status_code == 200:
                    data = response.json()
                    return self._convert_acled_events(data.get("events", []))
        except Exception as e:
            print(f"Error fetching ACLED events: {e}")
        return []

    def _convert_acled_events(self, events: List[Dict]) -> List[Dict[str, Any]]:
        """转换ACLED事件格式"""
        result = []
        for e in events:
            location = e.get("location", {})
            result.append({
                "id": e.get("id", f"acled-{datetime.now().timestamp()}"),
                "title": f"{e.get('eventType', 'Conflict')} in {e.get('country', 'Unknown')}",
                "description": f"Actors: {', '.join(e.get('actors', []))}. Fatalities: {e.get('fatalities', 0)}",
                "category": "conflict",
                "severity": min(5, max(3, 3 + (e.get("fatalities", 0) // 10))),
                "location": {
                    "country": e.get("country", ""),
                    "region": e.get("admin1", ""),
                    "lat": location.get("latitude", 0),
                    "lon": location.get("longitude", 0)
                },
                "timestamp": datetime.fromtimestamp(e.get("occurredAt", 0) / 1000).isoformat() + "Z" if e.get("occurredAt") else datetime.utcnow().isoformat() + "Z",
                "source": e.get("source", "ACLED"),
                "entities": e.get("actors", []),
                "sentiment": "negative"
            })
        return result

    # ============ Prediction Markets (Polymarket) ============

    async def fetch_polymarket_events(
        self,
        category: Optional[str] = None,
        query: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """获取Polymarket预测市场数据"""
        try:
            async with self._get_client() as client:
                payload = {
                    "pagination": {"pageSize": limit, "cursor": ""}
                }
                if category:
                    payload["category"] = category
                if query:
                    payload["query"] = query

                response = await client.post(
                    f"{self.base_url}/api/prediction/v1/list-prediction-markets",
                    json=payload
                )

                if response.status_code == 200:
                    data = response.json()
                    return self._convert_prediction_markets(data.get("markets", []))
        except Exception as e:
            print(f"Error fetching prediction markets: {e}")
        return []

    def _convert_prediction_markets(self, markets: List[Dict]) -> List[Dict[str, Any]]:
        """转换预测市场数据"""
        result = []
        for m in markets:
            yes_price = m.get("yesPrice", 0.5)
            # Determine severity based on probability extremes
            severity = 3
            if yes_price > 0.8 or yes_price < 0.2:
                severity = 4
            elif yes_price > 0.6 or yes_price < 0.4:
                severity = 3

            result.append({
                "id": m.get("id", f"pm-{datetime.now().timestamp()}"),
                "title": m.get("title", ""),
                "description": f"Prediction market with {yes_price*100:.1f}% probability",
                "category": self._map_prediction_category(m.get("category", "")),
                "severity": severity,
                "location": {"country": "Global", "region": "", "lat": 0, "lon": 0},
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "source": "Polymarket",
                "entities": [],
                "sentiment": "neutral",
                "prediction_data": {
                    "yes_price": yes_price,
                    "volume": m.get("volume", 0),
                    "url": m.get("url", "")
                }
            })
        return result

    def _map_prediction_category(self, cat: str) -> str:
        """映射预测市场类别"""
        category_map = {
            "geopolitics": "politics",
            "politics": "politics",
            "economy": "economy",
            "finance": "economy",
            "technology": "technology",
            "sports": "other"
        }
        return category_map.get(cat.lower(), "other")

    # ============ Intelligence Signals ============

    async def fetch_intelligence_signals(
        self,
        country_code: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """获取情报信号"""
        try:
            async with self._get_client() as client:
                # Try to get risk scores
                payload = {}
                if country_code:
                    payload["countryCode"] = country_code

                response = await client.post(
                    f"{self.base_url}/api/intelligence/v1/get-risk-scores",
                    json=payload
                )

                if response.status_code == 200:
                    data = response.json()
                    return self._convert_intelligence_data(data)
        except Exception as e:
            print(f"Error fetching intelligence: {e}")
        return []

    def _convert_intelligence_data(self, data: Dict) -> List[Dict[str, Any]]:
        """转换情报数据"""
        result = []
        # Convert risk scores if available
        scores = data.get("scores", [])
        for score in scores:
            result.append({
                "id": f"intel-{score.get('countryCode', 'unknown')}",
                "title": f"Risk Assessment: {score.get('countryName', score.get('countryCode', 'Unknown'))}",
                "description": f"Overall risk score: {score.get('overallScore', 0)}",
                "category": "politics",
                "severity": min(5, max(1, int(score.get("overallScore", 0) * 5))),
                "location": {"country": score.get("countryName", ""), "region": "", "lat": 0, "lon": 0},
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "source": "Intelligence",
                "entities": [],
                "sentiment": "neutral"
            })
        return result

    # ============ Combined Events Fetch ============

    async def fetch_events(
        self,
        category: Optional[str] = None,
        limit: int = 50,
        time_range: str = "24h"
    ) -> Dict[str, Any]:
        """
        获取所有事件数据

        Args:
            category: 事件类别
            limit: 返回数量
            time_range: 时间范围

        Returns:
            包含events和predictions的字典
        """
        events = []
        predictions = []

        # Fetch conflict events
        try:
            conflict_events = await self.fetch_conflict_events(limit=limit//2)
            events.extend(conflict_events)
        except Exception:
            pass

        # Fetch prediction markets
        try:
            prediction_markets = await self.fetch_polymarket_events(category=category, limit=limit//2)
            predictions.extend(prediction_markets)
            # Also add predictions as events
            events.extend(prediction_markets)
        except Exception:
            pass

        # Filter by category if specified
        if category:
            events = [e for e in events if e.get("category") == category]

        return {
            "events": events[:limit],
            "predictions": predictions[:limit],
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": "WorldMonitor"
        }

    async def get_event_summary(self) -> Dict[str, Any]:
        """获取事件摘要"""
        events_data = await self.fetch_events(limit=10)
        predictions = await self.fetch_polymarket_events(limit=5)

        return {
            "events_count": len(events_data.get("events", [])),
            "predictions_count": len(predictions),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "sources": ["conflict", "prediction", "intelligence"],
            "connected": self._connected
        }


# 全局服务实例
worldmonitor_service = WorldMonitorService()
