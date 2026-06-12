import axios from 'axios';

const client = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to attach JWT token
client.interceptors.request.use(
  (config) => {
    const tokensStr = localStorage.getItem('ssh_manager_tokens');
    if (tokensStr) {
      try {
        const tokens = JSON.parse(tokensStr);
        if (tokens.access_token) {
          config.headers.Authorization = `Bearer ${tokens.access_token}`;
        }
      } catch (e) {
        // Ignore parsing errors
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle auto token refresh on 401
client.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    // Check if error is 401 and not already retried
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      const tokensStr = localStorage.getItem('ssh_manager_tokens');
      if (tokensStr) {
        try {
          const tokens = JSON.parse(tokensStr);
          if (tokens.refresh_token) {
            // Attempt token refresh
            const refreshRes = await axios.post('/api/v1/auth/refresh', {
              refresh_token: tokens.refresh_token,
            });
            
            if (refreshRes.status === 200 && refreshRes.data.access_token) {
              const newTokens = {
                access_token: refreshRes.data.access_token,
                refresh_token: tokens.refresh_token,
              };
              localStorage.setItem('ssh_manager_tokens', JSON.stringify(newTokens));
              
              // Retry original request with new token
              originalRequest.headers.Authorization = `Bearer ${refreshRes.data.access_token}`;
              return client(originalRequest);
            }
          }
        } catch (refreshError) {
          // Refresh failed, log out user
          localStorage.removeItem('ssh_manager_tokens');
          localStorage.removeItem('ssh_manager_profile');
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);

export default client;
