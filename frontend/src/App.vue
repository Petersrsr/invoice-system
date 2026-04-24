<script setup lang="ts">
// App 仅负责站点级导航与路由出口，具体业务页面在 views 下维护。
</script>

<template>
  <main class="min-h-screen bg-slate-50 px-6 py-10">
    <div class="mx-auto max-w-6xl">
      <header class="mb-8 rounded-2xl bg-white p-6 shadow-sm">
        <h1 class="text-3xl font-bold tracking-tight text-slate-800">企业自动化发票报销系统</h1>
        <p class="mt-2 text-slate-500">员工上传发票，会计查看汇总与详情。</p>

        <nav class="mt-5 flex gap-3">
          <RouterLink
            to="/employee"
            class="rounded-lg border border-slate-300 px-4 py-2 text-sm text-slate-700 hover:bg-slate-100"
            active-class="border-indigo-600 bg-indigo-50 text-indigo-700"
          >
            员工页
          </RouterLink>
          <RouterLink
            to="/accounting"
            class="rounded-lg border border-slate-300 px-4 py-2 text-sm text-slate-700 hover:bg-slate-100"
            active-class="border-indigo-600 bg-indigo-50 text-indigo-700"
          >
            会计页
          </RouterLink>
        </nav>
      </header>

      <RouterView />
    </div>
  </main>
</template>
