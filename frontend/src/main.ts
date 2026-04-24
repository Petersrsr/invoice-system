import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import "./style.css";

// 应用启动时注入路由，用于员工页/会计页分离。
createApp(App).use(router).mount("#app");
