<script setup lang="ts">
import { ref, onMounted, onUnmounted } from "vue";

const backendStatus = ref<"checking" | "online" | "offline">("checking");
let timer: ReturnType<typeof setInterval>;

async function checkHealth() {
  try {
    const base = `${window.location.protocol}//${window.location.hostname}:8000`;
    const resp = await fetch(`${base}/health`, { signal: AbortSignal.timeout(5000) });
    backendStatus.value = resp.ok ? "online" : "offline";
  } catch {
    backendStatus.value = "offline";
  }
}

onMounted(() => {
  checkHealth();
  timer = setInterval(checkHealth, 10000);
});
onUnmounted(() => clearInterval(timer));
</script>

<template>
  <main class="min-h-screen bg-gradient-to-b from-slate-100 to-slate-50 px-4 py-8 md:px-6 md:py-10">
    <div class="mx-auto max-w-6xl">
      <header class="mb-6 rounded-2xl bg-white p-5 shadow-sm md:mb-8 md:p-6">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-bold tracking-tight text-slate-800 md:text-3xl">企业自动化发票报销系统</h1>
            <p class="mt-2 text-sm text-slate-500 md:text-base">员工上传发票，会计查看汇总与统计。</p>
          </div>
          <nav class="flex items-center gap-3">
            <span
              class="inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-medium"
              :class="{
                'bg-green-100 text-green-700': backendStatus === 'online',
                'bg-red-100 text-red-700': backendStatus === 'offline',
                'bg-yellow-100 text-yellow-700': backendStatus === 'checking',
              }"
            >
              <span
                class="h-1.5 w-1.5 rounded-full"
                :class="{
                  'bg-green-500': backendStatus === 'online',
                  'bg-red-500': backendStatus === 'offline',
                  'bg-yellow-500 animate-pulse': backendStatus === 'checking',
                }"
              ></span>
              {{ backendStatus === "online" ? "后端已连接" : backendStatus === "offline" ? "后端离线" : "检测中..." }}
            </span>
            <RouterLink
              to="/employee"
              class="rounded-lg px-4 py-2 text-sm font-medium transition-colors"
              :class="$route.name === 'employee' ? 'bg-indigo-600 text-white' : 'text-slate-600 hover:bg-slate-100'"
            >
              员工上传
            </RouterLink>
            <RouterLink
              to="/accounting"
              class="rounded-lg px-4 py-2 text-sm font-medium transition-colors"
              :class="$route.name === 'accounting' ? 'bg-indigo-600 text-white' : 'text-slate-600 hover:bg-slate-100'"
            >
              会计审批
            </RouterLink>
          </nav>
        </div>
      </header>

      <RouterView />
    </div>
  </main>
</template>
