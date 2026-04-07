import { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from 'react';
import { authApi, type AuthUser } from '../services/authApi';

interface AuthState {
  user: AuthUser | null;
  isLoading: boolean;
  isAuthenticated: boolean;
}

interface AuthContextType extends AuthState {
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  showLoginModal: boolean;
  setShowLoginModal: (show: boolean) => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>({
    user: null,
    isLoading: true,
    isAuthenticated: false,
  });
  const [showLoginModal, setShowLoginModal] = useState(false);

  // Auto-restore session on mount
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      setState({ user: null, isLoading: false, isAuthenticated: false });
      return;
    }
    authApi.getMe()
      .then((user) => {
        setState({ user, isLoading: false, isAuthenticated: true });
      })
      .catch(() => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        setState({ user: null, isLoading: false, isAuthenticated: false });
      });
  }, []);

  const login = useCallback(async (username: string, password: string) => {
    const res = await authApi.login(username, password);
    setState({ user: res.user, isLoading: false, isAuthenticated: true });
    setShowLoginModal(false);
  }, []);

  const register = useCallback(async (username: string, email: string, password: string) => {
    const res = await authApi.register(username, email, password);
    setState({ user: res.user, isLoading: false, isAuthenticated: true });
    setShowLoginModal(false);
  }, []);

  const logout = useCallback(async () => {
    await authApi.logout();
    setState({ user: null, isLoading: false, isAuthenticated: false });
  }, []);

  return (
    <AuthContext.Provider value={{ ...state, login, register, logout, showLoginModal, setShowLoginModal }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
