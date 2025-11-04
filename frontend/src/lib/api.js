import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

// Request interceptor - Add auth token and organization ID
api.interceptors.request.use(
  (config) => {
    // Get access token from localStorage
    const accessToken = localStorage.getItem('access_token');
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }

    // Get current organization ID
    const organizationId = localStorage.getItem('current_organization_id');
    if (organizationId && !config.url.includes('/auth/') && !config.url.includes('/organizations/')) {
      config.headers['X-Organization-Id'] = organizationId;
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - Handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If error is 401 and we haven't tried to refresh yet
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        
        if (!refreshToken) {
          throw new Error('No refresh token available');
        }

        // Try to refresh the token
        const response = await axios.post(
          `${API_BASE_URL}/auth/refresh/`,
          { refresh_token: refreshToken }
        );

        const { access_token, refresh_token: newRefreshToken } = response.data;

        // Update stored tokens
        localStorage.setItem('access_token', access_token);
        localStorage.setItem('refresh_token', newRefreshToken);

        // Retry the original request
        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        return api(originalRequest);
      } catch (refreshError) {
        // Refresh failed - clear tokens and redirect to login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        localStorage.removeItem('current_organization_id');
        
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// Authentication API
export const authAPI = {
  register: (data) => api.post('/auth/register/', data),
  login: (data) => api.post('/auth/login/', data),
  logout: (refreshToken) => api.post('/auth/logout/', { refresh_token: refreshToken }),
  verifyEmail: (token) => api.post('/auth/verify-email/', { token }),
  forgotPassword: (email) => api.post('/auth/forgot-password/', { email }),
  resetPassword: (data) => api.post('/auth/reset-password/', data),
  changePassword: (data) => api.post('/auth/change-password/', data),
  getProfile: () => api.get('/auth/profile/'),
  updateProfile: (data) => api.patch('/auth/profile/', data),
};

// Organizations API
export const organizationsAPI = {
  list: () => api.get('/organizations/'),
  create: (data) => api.post('/organizations/', data),
  get: (id) => api.get(`/organizations/${id}/`),
  update: (id, data) => api.patch(`/organizations/${id}/`, data),
  delete: (id) => api.delete(`/organizations/${id}/`),
  
  // Members
  listMembers: (orgId) => api.get(`/organizations/${orgId}/members/`),
  inviteMember: (orgId, data) => api.post(`/organizations/${orgId}/invite/`, data),
  updateMember: (orgId, memberId, data) => api.patch(`/organizations/${orgId}/members/${memberId}/`, data),
  removeMember: (orgId, memberId) => api.delete(`/organizations/${orgId}/members/${memberId}/`),
  
  // Invitations
  listInvitations: (orgId) => api.get(`/organizations/${orgId}/invitations/`),
  acceptInvitation: (token) => api.post('/organizations/invitations/accept/', { token }),
};

// Roles & Permissions API
export const rolesAPI = {
  list: () => api.get('/organizations/roles/'),
  listPermissions: () => api.get('/organizations/permissions/'),
};

export default api;