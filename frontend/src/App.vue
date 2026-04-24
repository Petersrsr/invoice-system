<script setup lang="ts">
// App 仅负责站点级导航与路由出口，具体业务页面在 views 下维护。
</script>

<template>
  <main class="min-h-screen bg-slate-50 px-6 py-10">
    <div class="mx-auto max-w-6xl">
      <header class="mb-8 rounded-2xl bg-white p-6 shadow-sm">
        <h1 class="text-3xl font-bold tracking-tight text-slate-800">企业自动化发票报销系统</h1>
        <p class="mt-2 text-slate-500">页面已独立：员工页与会计页不提供互相跳转入口。</p>
      </header>

      <RouterView />
    </div>
  </main>
</template>
