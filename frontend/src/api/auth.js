import client from './client';

export const authApi = {
  // Get current user
  getCurrentUser: async () => {
    const response = await client.get('/auth/me');
    return response.data;
  },

  // Logout
  logout: async () => {
    const response = await client.post('/auth/logout');
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    return response.data;
  },

  // Google login URL
  getGoogleLoginUrl: () => {
    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';
    return `${apiUrl}/auth/google/login`;
  },

  // Facebook connect URL
  getFacebookConnectUrl: () => {
    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';
    return `${apiUrl}/auth/facebook/connect`;
  },
};

export default authApi;
