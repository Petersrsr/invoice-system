/** @type {import('tailwindcss').Config} */
// Tailwind 扫描范围覆盖 index 与 src 下所有组件文件。
export default {
  content: ["./index.html", "./src/**/*.{vue,js,ts,jsx,tsx}"],
  theme: {
    extend: {},
  },
  plugins: [],
};
