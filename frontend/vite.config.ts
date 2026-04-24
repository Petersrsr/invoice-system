import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

// Vite 开发服务配置：默认端口 5173。
export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
  },
});
