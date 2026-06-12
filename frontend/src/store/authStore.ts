import { create } from 'zustand';
import client from '../api/client';

interface AdminProfile {
  id: string;
  username: string;
  email: string;
  role: string;
  permissions: string[];
  totp_enabled: boolean;
}

interface AuthState {
  profile: AdminProfile | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  setProfile: (profile: AdminProfile | null) => void;
  login: (username: string, password: string, totpCode?: string) => Promise<boolean>;
  logout: () => void;
  fetchProfile: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  profile: (() => {
    const p = localStorage.getItem('ssh_manager_profile');
    return p ? JSON.parse(p) : null;
  })(),
  isAuthenticated: !!localStorage.getItem('ssh_manager_tokens'),
  isLoading: false,
  error: null,

  setProfile: (profile) => set({ profile, isAuthenticated: !!profile }),

  login: async (username, password, totpCode) => {
    set({ isLoading: true, error: null });
    try {
      const res = await client.post('/auth/login-json', {
        username,
        password,
        totp_code: totpCode || null,
      });

      if (res.status === 200 && res.data.access_token) {
        localStorage.setItem('ssh_manager_tokens', JSON.stringify(res.data));
        
        // Fetch profile details
        set({ isAuthenticated: true });
        await get().fetchProfile();
        set({ isLoading: false });
        return true;
      }
      return false;
    } catch (e: any) {
      const errorMsg = e.response?.data?.detail || 'Login failed. Please check credentials.';
      set({ error: errorMsg, isLoading: false, isAuthenticated: false });
      return false;
    }
  },

  logout: () => {
    localStorage.removeItem('ssh_manager_tokens');
    localStorage.removeItem('ssh_manager_profile');
    set({ profile: null, isAuthenticated: false });
  },

  fetchProfile: async () => {
    try {
      const res = await client.get('/auth/me');
      if (res.status === 200) {
        localStorage.setItem('ssh_manager_profile', JSON.stringify(res.data));
        set({ profile: res.data, isAuthenticated: true });
      }
    } catch (e) {
      get().logout();
    }
  },
}));
