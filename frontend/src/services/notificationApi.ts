/**
 * notificationApi - 通知 API 调用
 */
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8005';

export interface Notification {
  id: string;
  notification_type: string;
  title: string;
  message: string;
  data: Record<string, any>;
  is_read: boolean;
  created_at: string;
  read_at: string | null;
}

export interface NotificationListResponse {
  notifications: Notification[];
  total: number;
  unread_count: number;
}

function getToken(): string | null {
  return localStorage.getItem('access_token');
}

async function request(path: string, options: RequestInit = {}) {
  const token = getToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE_URL}${path}`, { ...options, headers });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed: ${res.status}`);
  }
  return res.json();
}

export const notificationApi = {
  async list(unreadOnly = false, limit = 20, offset = 0): Promise<NotificationListResponse> {
    return request(
      `/api/v1/notifications?unread_only=${unreadOnly}&limit=${limit}&offset=${offset}`
    );
  },

  async getUnreadCount(): Promise<{ unread_count: number }> {
    return request('/api/v1/notifications/unread-count');
  },

  async markRead(notificationId: string): Promise<{ success: boolean }> {
    return request(`/api/v1/notifications/${notificationId}/read`, { method: 'POST' });
  },

  async markAllRead(): Promise<{ marked_count: number }> {
    return request('/api/v1/notifications/mark-all-read', { method: 'POST' });
  },

  async deleteNotification(notificationId: string): Promise<{ success: boolean }> {
    return request(`/api/v1/notifications/${notificationId}`, { method: 'DELETE' });
  },
};
