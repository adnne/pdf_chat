import axios from "axios";
import router from "../router";

const api = axios.create({
  baseURL: "http://localhost:8000/api",
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor to add JWT token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If the error is 401 and we haven't retried yet
    if (error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        // Try to refresh the token
        const refreshToken = localStorage.getItem("refresh_token");
        const response = await axios.post(
          "http://localhost:8000/api/auth/token/refresh/",
          {
            refresh: refreshToken,
          }
        );

        const { access } = response.data;
        localStorage.setItem("access_token", access);

        // Retry the original request with the new token
        originalRequest.headers.Authorization = `Bearer ${access}`;
        return api(originalRequest);
      } catch (refreshError) {
        // If refresh fails, redirect to login
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        router.push("/login");
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export const login = async (email: string, password: string) => {
  const response = await api.post("/auth/login/", { email, password });
  const { access, refresh } = response.data;
  localStorage.setItem("access_token", access);
  localStorage.setItem("refresh_token", refresh);
  return response.data;
};

export const logout = async () => {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
  await api.post("/auth/logout/");
};

export default api;
