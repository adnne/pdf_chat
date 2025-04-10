import {
  createRouter,
  createWebHistory,
  type RouteRecordRaw,
  type NavigationGuardNext,
  type RouteLocationNormalized,
} from "vue-router";
import Dashboard from "../views/Dashboard.vue";
import Login from "../views/Login.vue";

const routes: RouteRecordRaw[] = [
  {
    path: "/",
    name: "dashboard",
    component: Dashboard,
    meta: { requiresAuth: true },
  },
  {
    path: "/login",
    name: "login",
    component: Login,
    meta: { guest: true },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Navigation guard for authentication
router.beforeEach(
  (
    to: RouteLocationNormalized,
    from: RouteLocationNormalized,
    next: NavigationGuardNext
  ) => {
    const isAuthenticated = localStorage.getItem("access_token");

    if (to.matched.some((record) => record.meta.requiresAuth)) {
      if (!isAuthenticated) {
        next({ name: "login" });
      } else {
        next();
      }
    } else if (
      to.matched.some((record) => record.meta.guest) &&
      isAuthenticated
    ) {
      next({ name: "dashboard" });
    } else {
      next();
    }
  }
);

export default router;
