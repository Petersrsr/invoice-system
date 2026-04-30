import { createRouter, createWebHistory } from "vue-router";

import AccountantPage from "./views/AccountantPage.vue";
import EmployeePage from "./views/EmployeePage.vue";

// 前端路由：默认进入员工页，保持上传流程更直接。
const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", redirect: "/employee" },
    { path: "/employee", name: "employee", component: EmployeePage },
    { path: "/accounting", name: "accounting", component: AccountantPage },
    { path: "/:pathMatch(.*)*", redirect: "/employee" },
  ],
});

export default router;
