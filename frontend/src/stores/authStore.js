import { create } from 'zustand';
import { authAPI } from '../lib/api';

const useAuthStore = create((set, get) => ({
  user: JSON.parse(localStorage.getItem('user')) || null,
  accessToken: localStorage.getItem('access_token') || null,
  refreshToken: localStorage.getItem('refresh_token') || null,
  isAuthenticated: !!localStorage.getItem('access_token'),
  loading: false,
  error: null,

  // Register new user
  register: async (data) => {
    set({ loading: true, error: null });
    try {
      const response = await authAPI.register(data);
      set({ loading: false });
      return response.data;
    } catch (error) {
      const errorMessage = error.response?.data?.error?.message || 'Registration failed';
      set({ loading: false, error: errorMessage });
      throw error;
    }
  },

  // Login user
  login: async (credentials) => {
    set({ loading: true, error: null });
    try {
      const response = await authAPI.login(credentials);
      const { access_token, refresh_token, user } = response.data;

      // Store tokens and user
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      localStorage.setItem('user', JSON.stringify(user));

      set({
        user,
        accessToken: access_token,
        refreshToken: refresh_token,
        isAuthenticated: true,
        loading: false,
        error: null,
      });

      return response.data;
    } catch (error) {
      const errorMessage = error.response?.data?.error?.message || 'Login failed';
      set({ loading: false, error: errorMessage });
      throw error;
    }
  },

  // Logout user
  logout: async () => {
    try {
      const refreshToken = get().refreshToken;
      if (refreshToken) {
        await authAPI.logout(refreshToken);
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Clear everything
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
      localStorage.removeItem('current_organization_id');

      set({
        user: null,
        accessToken: null,
        refreshToken: null,
        isAuthenticated: false,
        error: null,
      });
    }
  },

  // Update user profile
  updateUser: (user) => {
    localStorage.setItem('user', JSON.stringify(user));
    set({ user });
  },

  // Clear error
  clearError: () => set({ error: null }),
}));

export default useAuthStore;