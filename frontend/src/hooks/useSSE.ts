/**
 * useSSE - SSE 连接管理 Hook
 *
 * 自动重连（指数退避 1→2→4→8→30s），保持最近 100 条事件
 */
import { useState, useEffect, useRef, useCallback } from 'react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8005';

export interface SSEEvent {
  type: string;
  data: any;
  receivedAt: number;
}

interface SSEReturn {
  events: SSEEvent[];
  connected: boolean;
  lastEvent: SSEEvent | null;
  reconnectCount: number;
}

const MAX_EVENTS = 100;
const MAX_BACKOFF = 30000; // 30s cap

export function useSSE(_token?: string | null): SSEReturn {
  const [events, setEvents] = useState<SSEEvent[]>([]);
  const [connected, setConnected] = useState(false);
  const [lastEvent, setLastEvent] = useState<SSEEvent | null>(null);
  const [reconnectCount, setReconnectCount] = useState(0);
  const esRef = useRef<EventSource | null>(null);
  const backoffRef = useRef(1000);

  const connect = useCallback(() => {
    if (esRef.current) {
      esRef.current.close();
    }

    const url = `${API_BASE_URL}/api/v1/stream/events`;
    // Pass token as query param for EventSource (no custom header support)
    const token = localStorage.getItem('access_token');
    const finalUrl = token
      ? `${url}?token=${encodeURIComponent(token)}`
      : url;
    const es = new EventSource(finalUrl);
    esRef.current = es;

    es.onopen = () => {
      setConnected(true);
      backoffRef.current = 1000; // 重置退避
    };

    es.onmessage = (e) => {
      // 跳过心跳（以冒号开头的行不会触发 onmessage）
      if (!e.data) return;
      try {
        const parsed = JSON.parse(e.data);
        const sseEvent: SSEEvent = {
          type: parsed.type,
          data: parsed.data,
          receivedAt: Date.now(),
        };
        setLastEvent(sseEvent);
        setEvents(prev => {
          const next = [sseEvent, ...prev];
          return next.slice(0, MAX_EVENTS);
        });
      } catch {
        // ignore non-JSON messages
      }
    };

    es.onerror = () => {
      setConnected(false);
      es.close();
      esRef.current = null;

      // 指数退避重连
      const delay = backoffRef.current;
      backoffRef.current = Math.min(backoffRef.current * 2, MAX_BACKOFF);
      setReconnectCount(c => c + 1);

      setTimeout(() => {
        connect();
      }, delay);
    };
  }, []);

  useEffect(() => {
    connect();
    return () => {
      if (esRef.current) {
        esRef.current.close();
        esRef.current = null;
      }
    };
  }, [connect]);

  // 如果有 token，SSE 不支持自定义 header，
  // EventSource 的认证通常通过 query param 或 cookie
  // 这里不做 token 注入，服务端从 header 读取（SSE 连接建立时无法设置 header）
  // TODO: 可以改用 query param 方式传 token

  return { events, connected, lastEvent, reconnectCount };
}
