<script setup lang="ts">
// App 仅负责站点级导航与路由出口，具体业务页面在 views 下维护。
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
          <nav class="flex items-center gap-2">
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
