# 后台新闻抓取调度服务
"""
P2.3 实时数据：定时抓取 RSS + WorldMonitor，去重后推送给告警引擎和 SSE
"""
import asyncio
import logging
import uuid
from collections import deque
from datetime import datetime, timezone
from typing import Any, Callable, Deque, Dict, List, Optional, Set

from app.core.config import config

logger = logging.getLogger(__name__)


class NewsFetcherService:
    """单例：后台周期性抓取新闻并通知订阅者"""

    def __init__(self) -> None:
        self._seen_ids: Set[str] = set()
        self._max_seen: int = config.realtime.max_seen_events
        self._subscribers: List[Callable] = []
        self._rss_task: Optional[asyncio.Task] = None
        self._wm_task: Optional[asyncio.Task] = None
        self._running = False

        # 统计信息
        self._last_rss_time: Optional[str] = None
        self._last_wm_time: Optional[str] = None
        self._total_events_fetched: int = 0
        self._recent_events: Deque[Dict[str, Any]] = deque(maxlen=100)

    # ── 生命周期 ──────────────────────────────────────────

    async def start(self) -> None:
        if not config.realtime.news_fetcher_enabled:
            logger.info("[NewsFetcher] disabled by config")
            return
        if self._running:
            return
        self._running = True
        self._rss_task = asyncio.create_task(self._fetch_rss_cycle())
        self._wm_task = asyncio.create_task(self._fetch_worldmonitor_cycle())
        logger.info(
            "[NewsFetcher] started (rss=%ds, wm=%ds)",
            config.realtime.rss_interval,
            config.realtime.worldmonitor_interval,
        )

    async def stop(self) -> None:
        self._running = False
        for task in (self._rss_task, self._wm_task):
            if task and not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        self._rss_task = None
        self._wm_task = None
        logger.info("[NewsFetcher] stopped")

    # ── 观察者 ────────────────────────────────────────────

    def subscribe(self, callback: Callable) -> None:
        self._subscribers.append(callback)

    def unsubscribe(self, callback: Callable) -> None:
        self._subscribers = [cb for cb in self._subscribers if cb is not callback]

    def _notify_subscribers(self, events: List[Dict[str, Any]]) -> None:
        for cb in self._subscribers:
            try:
                cb(events)
            except Exception as exc:
                logger.error("[NewsFetcher] subscriber error: %s", exc)

    # ── 抓取循环 ──────────────────────────────────────────

    async def _fetch_rss_cycle(self) -> None:
        """周期性调用 RSS 服务获取新闻"""
        while self._running:
            try:
                from app.services.rss_service import rss_service
                events = await rss_service.fetch_all_feeds(limit=100)
                new_events = self._deduplicate(events)
                if new_events:
                    self._process_new_events(new_events)
                self._last_rss_time = datetime.now(timezone.utc).isoformat()
                logger.info("[NewsFetcher] RSS cycle: %d total, %d new", len(events), len(new_events))
            except Exception as exc:
                logger.error("[NewsFetcher] RSS cycle error: %s", exc)

            await asyncio.sleep(config.realtime.rss_interval)

    async def _fetch_worldmonitor_cycle(self) -> None:
        """周期性调用 WorldMonitor 服务获取事件"""
        while self._running:
            try:
                from app.services.worldmonitor_service import worldmonitor_service
                result = await worldmonitor_service.fetch_events(limit=50)
                events = result.get("events", [])
                new_events = self._deduplicate(events)
                if new_events:
                    self._process_new_events(new_events)
                self._last_wm_time = datetime.now(timezone.utc).isoformat()
                logger.info("[NewsFetcher] WM cycle: %d total, %d new", len(events), len(new_events))
            except Exception as exc:
                logger.error("[NewsFetcher] WM cycle error: %s", exc)

            await asyncio.sleep(config.realtime.worldmonitor_interval)

    # ── 去重 ──────────────────────────────────────────────

    def _deduplicate(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        new_events = []
        for ev in events:
            ev_id = ev.get("id") or str(uuid.uuid4())
            if ev_id not in self._seen_ids:
                self._seen_ids.add(ev_id)
                ev["id"] = ev_id
                new_events.append(ev)

        # 防止集合无限增长
        if len(self._seen_ids) > self._max_seen:
            excess = len(self._seen_ids) - self._max_seen
            remove_ids = list(self._seen_ids)[:excess]
            for rid in remove_ids:
                self._seen_ids.discard(rid)

        return new_events

    # ── 处理新事件 ────────────────────────────────────────

    def _process_new_events(self, events: List[Dict[str, Any]]) -> None:
        self._total_events_fetched += len(events)
        for ev in events:
            self._recent_events.append(ev)

        # 推送给告警引擎
        try:
            from app.services.event_monitor_service import alert_engine
            alerts = alert_engine.process_events_batch(events)
            if alerts:
                logger.info("[NewsFetcher] %d alerts triggered", len(alerts))
        except Exception as exc:
            logger.error("[NewsFetcher] alert engine error: %s", exc)

        # 通知订阅者（SSE、通知服务等）
        self._notify_subscribers(events)

    # ── 状态查询 ──────────────────────────────────────────

    def get_status(self) -> Dict[str, Any]:
        return {
            "running": self._running,
            "last_rss_fetch": self._last_rss_time,
            "last_wm_fetch": self._last_wm_time,
            "total_events_fetched": self._total_events_fetched,
            "seen_ids_count": len(self._seen_ids),
            "recent_events_count": len(self._recent_events),
            "subscribers_count": len(self._subscribers),
        }


# 全局单例
news_fetcher_service = NewsFetcherService()
