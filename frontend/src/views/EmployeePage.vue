<script setup lang="ts">
import InvoiceUpload from "../components/InvoiceUpload.vue";

// 员工页只保留上传入口，不展示会计数据。
</script>

<template>
  <section class="rounded-2xl bg-white p-6 shadow-sm">
    <h2 class="mb-2 text-xl font-semibold text-slate-800">员工发票上传</h2>
    <p class="mb-6 text-sm text-slate-500">本页面仅提供上传能力，上传后会自动进入后台汇总。</p>
    <InvoiceUpload />
  </section>
</template>
