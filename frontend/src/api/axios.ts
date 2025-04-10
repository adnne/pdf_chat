import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000/api/",
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Handle refresh token flow
    if (error.response?.status === 401 && !originalRequest._retry) {
      const refreshToken = localStorage.getItem("refreshToken");

      if (refreshToken) {
        // Prevent infinite retry on refresh token endpoint
        if (originalRequest.url === "/auth/token/refresh/") {
          return Promise.reject(error);
        }

        originalRequest._retry = true;

        try {
          const response = await api.post("/auth/token/refresh/", {
            refresh: refreshToken,
          });

          const { access } = response.data;
          localStorage.setItem("token", access);
          originalRequest.headers.Authorization = `Bearer ${access}`;

          return api(originalRequest);
        } catch (refreshError) {
          // If refresh token is invalid, clear auth and redirect to login
          localStorage.removeItem("token");
          localStorage.removeItem("refreshToken");
          window.location.href = "/login";
          return Promise.reject(refreshError);
        }
      }
    }

    // Handle other 401 errors (no refresh token)
    if (error.response?.status === 401) {
      localStorage.removeItem("token");
      localStorage.removeItem("refreshToken");
      window.location.href = "/login";
    }

    return Promise.reject(error);
  }
);

export default api;
