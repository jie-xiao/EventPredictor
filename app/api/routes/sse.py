# SSE (Server-Sent Events) 端点
"""
P2.3 实时数据：SSE 推送端点 + 连接管理器
"""
import asyncio
import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from app.core.config import config
from app.core.auth_deps import get_optional_user

logger = logging.getLogger(__name__)
router = APIRouter(tags=["sse"])


class SSEConnectionManager:
    """管理所有 SSE 客户端连接"""

    def __init__(self, max_connections: int = 50):
        self._max = max_connections
        # client_id -> asyncio.Queue
        self._connections: Dict[str, asyncio.Queue] = {}
        # user_id -> set[client_id]  (用于定向推送)
        self._user_connections: Dict[str, set] = {}

    @property
    def connection_count(self) -> int:
        return len(self._connections)

    def connect(self, client_id: str, user_id: Optional[str] = None) -> asyncio.Queue:
        if len(self._connections) >= self._max:
            # 踢掉最旧的连接
            oldest = next(iter(self._connections), None)
            if oldest:
                self.disconnect(oldest)

        q: asyncio.Queue = asyncio.Queue(maxsize=256)
        self._connections[client_id] = q

        if user_id:
            if user_id not in self._user_connections:
                self._user_connections[user_id] = set()
            self._user_connections[user_id].add(client_id)

        logger.info("[SSE] client %s connected (total=%d)", client_id, len(self._connections))
        return q

    def disconnect(self, client_id: str) -> None:
        q = self._connections.pop(client_id, None)
        if q is not None:
            # 唤醒等待的消费者让它退出
            q.put_nowait(None)
        # 从 user_connections 中移除
        for uid, cids in list(self._user_connections.items()):
            cids.discard(client_id)
            if not cids:
                del self._user_connections[uid]
        logger.info("[SSE] client %s disconnected (total=%d)", client_id, len(self._connections))

    async def broadcast(self, event_type: str, data: Any) -> None:
        """广播到所有连接"""
        message = json.dumps({"type": event_type, "data": data}, ensure_ascii=False, default=str)
        disconnected = []
        for cid, q in self._connections.items():
            try:
                q.put_nowait(message)
            except asyncio.QueueFull:
                disconnected.append(cid)
        for cid in disconnected:
            # Clean up queue independently instead of calling disconnect()
            # to avoid side effects on _user_connections for multi-connection users.
            q = self._connections.pop(cid, None)
            if q:
                q.put_nowait(None)
            for uid, cids in list(self._user_connections.items()):
                cids.discard(cid)
                if not cids:
                    del self._user_connections[uid]

    async def send_to_user(self, user_id: str, event_type: str, data: Any) -> None:
        """定向推送到特定用户的连接"""
        cids = self._user_connections.get(user_id, set())
        message = json.dumps({"type": event_type, "data": data}, ensure_ascii=False, default=str)
        for cid in list(cids):
            q = self._connections.get(cid)
            if q:
                try:
                    q.put_nowait(message)
                except asyncio.QueueFull:
                    # Same safe cleanup as broadcast — avoid disconnect side-effects
                    q = self._connections.pop(cid, None)
                    if q:
                        q.put_nowait(None)

# 全局实例
sse_manager = SSEConnectionManager(max_connections=config.realtime.sse_max_connections)


async def _sse_generator(request: Request, queue: asyncio.Queue) -> Any:
    """SSE 事件生成器"""
    heartbeat_interval = config.realtime.sse_heartbeat
    try:
        while True:
            if await request.is_disconnected():
                break
            try:
                message = await asyncio.wait_for(queue.get(), timeout=heartbeat_interval)
                if message is None:
                    break
                yield f"data: {message}\n\n"
            except asyncio.TimeoutError:
                # 心跳
                yield ": heartbeat\n\n"
    except asyncio.CancelledError:
        pass


@router.get("/api/v1/stream/events")
async def stream_events(request: Request):
    """
    SSE 端点：实时事件流

    可选：Bearer token → 启用用户定向通知
    格式: data: {"type": "new_event|alert|notification", "data": {...}}\n\n
    """
    # 尝试识别用户
    user_id: Optional[str] = None
    auth_header = request.headers.get("authorization", "")
    if auth_header.startswith("Bearer "):
        try:
            from app.core.security import decode_token
            token = auth_header[7:]
            payload = decode_token(token)
            if payload and payload.get("type") == "access":
                user_id = payload.get("sub")
        except Exception:
            pass

    # Also check query param for EventSource connections (no custom headers)
    if not user_id:
        query_token = request.query_params.get("token", "")
        if query_token:
            try:
                from app.core.security import decode_token
                payload = decode_token(query_token)
                if payload and payload.get("type") == "access":
                    user_id = payload.get("sub")
            except Exception:
                pass

    client_id = str(uuid.uuid4())
    queue = sse_manager.connect(client_id, user_id)

    async def on_disconnect():
        sse_manager.disconnect(client_id)

    response = StreamingResponse(
        _sse_generator(request, queue),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "Access-Control-Allow-Origin": "*",
        },
    )

    # 注册断开回调
    request.state._sse_disconnect = on_disconnect

    return response


# ── 订阅 news_fetcher_service 的新事件 ──────────────────

def _on_new_events(events: list) -> None:
    """同步回调，由 news_fetcher_service 调用"""
    import asyncio
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return
    for ev in events:
        loop.create_task(sse_manager.broadcast("new_event", ev))


# 注册订阅（在模块加载时）
def _setup_subscription():
    from app.services.news_fetcher_service import news_fetcher_service
    news_fetcher_service.subscribe(_on_new_events)

_setup_subscription()
