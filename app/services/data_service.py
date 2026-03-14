# 数据获取服务 - 优先实时数据源 (RSS > Polymarket > WorldMonitor > 内置数据)
import json
import os
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from app.api.models import Event


class DataService:
    """数据获取服务 - 优先实时数据源，内置数据仅作为fallback

    数据源优先级:
    1. RSS Feeds (实时新闻) - 最高优先级
    2. Polymarket (预测市场) - 次高优先级
    3. WorldMonitor API (集成数据) - 第三优先级
    4. 内置事件数据 (events.json) - 仅作为 fallback
    """

    def __init__(self):
        self._events: List[Dict[str, Any]] = []
        self._last_refresh: Optional[datetime] = None
        self._data_source: str = "none"

        # 延迟加载的服务实例
        self._rss_service = None
        self._polymarket_service = None
        self._worldmonitor_service = None

        # 先加载内置数据作为初始fallback
        self._load_preset_events()

    # ============ 服务延迟加载 ============

    async def _get_rss_service(self):
        """获取RSS服务实例（延迟加载）"""
        if self._rss_service is None:
            try:
                from app.services.rss_service import rss_service
                self._rss_service = rss_service
            except ImportError:
                pass
        return self._rss_service

    async def _get_polymarket_service(self):
        """获取Polymarket服务实例（延迟加载）"""
        if self._polymarket_service is None:
            try:
                from app.services.polymarket_service import polymarket_service
                self._polymarket_service = polymarket_service
            except ImportError:
                pass
        return self._polymarket_service

    async def _get_worldmonitor_service(self):
        """获取WorldMonitor服务实例（延迟加载）"""
        if self._worldmonitor_service is None:
            try:
                from app.services.worldmonitor_service import worldmonitor_service
                self._worldmonitor_service = worldmonitor_service
            except ImportError:
                pass
        return self._worldmonitor_service

    # ============ 内置数据加载 ============

    def _load_preset_events(self):
        """加载预置事件数据（仅作为fallback）"""
        possible_paths = [
            os.path.join(os.path.dirname(__file__), "..", "..", "data", "events.json"),
            os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "events.json"),
            "E:\\EventPredictor\\data\\events.json",
            "data/events.json"
        ]

        for path in possible_paths:
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        self._events = data.get("events", [])
                        self._last_refresh = datetime.now()
                        print(f"[Fallback] Loaded {len(self._events)} preset events from {path}")
                        return
                except Exception as e:
                    print(f"Failed to load {path}: {e}")
                    continue

        print("Warning: No preset events found")
        self._events = []

    # ============ 主数据获取方法 ============

    async def get_events(
        self,
        category: Optional[str] = None,
        limit: int = 20,
        time_range: str = "24h"
    ) -> List[Event]:
        """
        获取事件列表 - 优先从实时数据源获取

        Args:
            category: 事件类别过滤
            limit: 返回数量限制
            time_range: 时间范围 (1h, 6h, 24h, 7d, 30d, all)

        Returns:
            事件列表
        """
        # 如果数据过期或为空，刷新数据
        if self._should_refresh():
            await self.refresh_data()

        filtered_events = self._events.copy()

        # 按类别过滤
        if category:
            filtered_events = [e for e in filtered_events if e.get("category") == category]

        # 按时间范围过滤
        if time_range != "all":
            hours = self._parse_time_range(time_range)
            cutoff_time = datetime.now().astimezone() - timedelta(hours=hours)

            filtered_events = [
                e for e in filtered_events
                if self._parse_timestamp(e.get("timestamp", "")) >= cutoff_time
            ]

        # 按严重程度排序（倒序）
        filtered_events.sort(key=lambda x: x.get("severity", 0), reverse=True)

        # 限制数量
        filtered_events = filtered_events[:limit]

        # 转换为Event对象
        return [self._dict_to_event(e) for e in filtered_events]

    def _should_refresh(self) -> bool:
        """检查是否需要刷新数据"""
        if not self._events:
            return True
        if not self._last_refresh:
            return True
        # 5分钟刷新一次
        return (datetime.now() - self._last_refresh).seconds > 300

    # ============ 数据刷新 - 核心逻辑 ============

    async def refresh_data(self) -> bool:
        """
        刷新数据 - 按优先级从多个数据源获取

        优先级: RSS > Polymarket > WorldMonitor > 内置数据
        """
        all_events = []
        sources_status = {}

        # 1. 尝试从 RSS 获取数据（最高优先级）
        try:
            rss_service = await self._get_rss_service()
            if rss_service:
                rss_events = await rss_service.fetch_all_feeds(limit=100)
                if rss_events:
                    all_events.extend(rss_events)
                    sources_status["rss"] = len(rss_events)
                    print(f"[RSS] Fetched {len(rss_events)} events")
        except Exception as e:
            print(f"[RSS] Error: {e}")
            sources_status["rss"] = 0

        # 2. 尝试从 Polymarket 获取预测市场数据
        try:
            pm_service = await self._get_polymarket_service()
            if pm_service:
                pm_events = await pm_service.get_trending_markets(limit=30)
                pm_politics = await pm_service.get_politics_markets(limit=20)

                if pm_events:
                    all_events.extend(pm_events)
                    sources_status["polymarket"] = len(pm_events)
                    print(f"[Polymarket] Fetched {len(pm_events)} markets")
                if pm_politics:
                    all_events.extend(pm_politics)
        except Exception as e:
            print(f"[Polymarket] Error: {e}")
            sources_status["polymarket"] = 0

        # 3. 尝试从 WorldMonitor 获取数据
        try:
            wm_service = await self._get_worldmonitor_service()
            if wm_service:
                wm_data = await wm_service.fetch_events(limit=50)
                if wm_data and wm_data.get("events"):
                    wm_events = wm_data["events"]
                    all_events.extend(wm_events)
                    sources_status["worldmonitor"] = len(wm_events)
                    print(f"[WorldMonitor] Fetched {len(wm_events)} events")
        except Exception as e:
            print(f"[WorldMonitor] Error: {e}")
            sources_status["worldmonitor"] = 0

        # 检查是否有任何实时数据
        has_live_data = sum(sources_status.values()) > 0

        if has_live_data:
            # 合并数据并去重
            self._events = self._deduplicate_events(all_events)
            self._data_source = "live"
            print(f"[Data] Using live data: {len(self._events)} events from {sources_status}")
        else:
            # Fallback 到内置数据
            self._load_preset_events()
            self._data_source = "fallback"
            print(f"[Data] Using fallback data: {len(self._events)} events")

        self._last_refresh = datetime.now()
        return True

    def _deduplicate_events(self, events: List[Dict]) -> List[Dict]:
        """去除重复事件（基于标题相似度）"""
        seen_titles = set()
        unique_events = []

        for event in events:
            title_lower = event.get("title", "").lower()[:50]
            if title_lower not in seen_titles:
                seen_titles.add(title_lower)
                unique_events.append(event)

        return unique_events

    # ============ 单事件查询 ============

    async def get_event_by_id(self, event_id: str) -> Optional[Event]:
        """根据ID获取事件"""
        if self._should_refresh():
            await self.refresh_data()

        for event_dict in self._events:
            if event_dict.get("id") == event_id:
                return self._dict_to_event(event_dict)
        return None

    # ============ 辅助方法 ============

    def get_categories(self) -> List[str]:
        """获取所有事件类别"""
        categories = set()
        for event in self._events:
            cat = event.get("category")
            if cat:
                categories.add(cat)
        return sorted(list(categories))

    def get_event_count(self) -> int:
        """获取事件总数"""
        return len(self._events)

    def get_data_source(self) -> str:
        """获取当前数据源类型"""
        return self._data_source

    async def get_source_status(self) -> Dict[str, Any]:
        """获取所有数据源状态"""
        status = {
            "current_source": self._data_source,
            "last_refresh": self._last_refresh.isoformat() if self._last_refresh else None,
            "event_count": len(self._events),
            "sources": {}
        }

        # RSS 状态
        try:
            rss = await self._get_rss_service()
            if rss:
                status["sources"]["rss"] = await rss.get_source_status()
        except Exception:
            status["sources"]["rss"] = {"available": False}

        # Polymarket 状态
        try:
            pm = await self._get_polymarket_service()
            if pm:
                status["sources"]["polymarket"] = await pm.get_service_status()
        except Exception:
            status["sources"]["polymarket"] = {"connected": False}

        # WorldMonitor 状态
        try:
            wm = await self._get_worldmonitor_service()
            if wm:
                connected = await wm.check_connection()
                status["sources"]["worldmonitor"] = {"connected": connected}
        except Exception:
            status["sources"]["worldmonitor"] = {"connected": False}

        return status

    def _parse_time_range(self, time_range: str) -> int:
        """解析时间范围字符串"""
        time_map = {
            "1h": 1,
            "6h": 6,
            "24h": 24,
            "48h": 48,
            "7d": 24 * 7,
            "30d": 24 * 30,
            "all": 24 * 365 * 100
        }
        return time_map.get(time_range, 24)

    def _parse_timestamp(self, timestamp: str) -> datetime:
        """解析时间戳"""
        try:
            if timestamp.endswith("Z"):
                timestamp = timestamp[:-1] + "+00:00"
            return datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except:
            return datetime.min

    def _dict_to_event(self, event_dict: Dict[str, Any]) -> Event:
        """将字典转换为Event对象"""
        location = event_dict.get("location", {})

        return Event(
            id=event_dict.get("id", ""),
            title=event_dict.get("title", ""),
            description=event_dict.get("description", ""),
            source=event_dict.get("source", "unknown"),
            timestamp=event_dict.get("timestamp", ""),
            category=event_dict.get("category", "other"),
            importance=event_dict.get("severity", 3),
            location=location if location else None,
            entities=event_dict.get("entities", []),
            sentiment=event_dict.get("sentiment", "neutral"),
            severity=event_dict.get("severity", None),
            category_label=event_dict.get("category_label", None),
            source_label=event_dict.get("source_label", None)
        )


# 全局服务实例
data_service = DataService()
