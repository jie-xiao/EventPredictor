// EventPredictor Auth API Service
const API_BASE = '/api/v1';

export interface AuthUser {
  id: string;
  username: string;
  email: string;
  display_name: string;
  avatar_url: string | null;
  is_active: boolean;
  created_at: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface LoginResponse extends AuthTokens {
  user: AuthUser;
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = localStorage.getItem('access_token');
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (!res.ok) {
    const data = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(data.detail || 'Request failed');
  }
  return res.json();
}

export const authApi = {
  async register(username: string, email: string, password: string): Promise<LoginResponse> {
    const data = await request<LoginResponse>('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ username, email, password }),
    });
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token);
    return data;
  },

  async login(username: string, password: string): Promise<LoginResponse> {
    const data = await request<LoginResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token);
    return data;
  },

  async refresh(): Promise<AuthTokens> {
    const refreshToken = localStorage.getItem('refresh_token');
    const data = await request<AuthTokens>('/auth/refresh', {
      method: 'POST',
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token);
    return data;
  },

  async getMe(): Promise<AuthUser> {
    return request<AuthUser>('/auth/me');
  },

  async logout(): Promise<void> {
    const refreshToken = localStorage.getItem('refresh_token');
    try {
      await request<void>('/auth/logout', {
        method: 'POST',
        body: JSON.stringify({ refresh_token: refreshToken }),
      });
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    }
  },
};
