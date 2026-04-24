/// <reference types="vite/client" />

// 声明 .vue 模块类型，供 TypeScript 正确识别单文件组件。
declare module "*.vue" {
  import type { DefineComponent } from "vue";
  const component: DefineComponent<Record<string, unknown>, Record<string, unknown>, unknown>;
  export default component;
}
