import { defineStore } from "pinia";
import { login as apiLogin, logout as apiLogout } from "../api";
import router from "../router";

interface AuthState {
  isAuthenticated: boolean;
  user: any | null;
}

export const useAuthStore = defineStore("auth", {
  state: (): AuthState => ({
    isAuthenticated: !!localStorage.getItem("access_token"),
    user: null,
  }),

  actions: {
    async login(email: string, password: string) {
      try {
        const data = await apiLogin(email, password);
        this.isAuthenticated = true;
        this.user = data.user;
        localStorage.setItem("access_token", data.access);
        localStorage.setItem("refresh_token", data.refresh);
        router.push("/");
      } catch (error) {
        console.error("Login failed:", error);
        throw error;
      }
    },

    async logout() {
      try {
        await apiLogout();
        this.isAuthenticated = false;
        this.user = null;
        router.push("/login");
      } catch (error) {
        console.error("Logout failed:", error);
        throw error;
      }
    },

    checkAuth() {
      const token = localStorage.getItem("access_token");
      this.isAuthenticated = !!token;
    },
  },

  getters: {
    isLoggedIn: (state) => state.isAuthenticated,
    currentUser: (state) => state.user,
  },
});
