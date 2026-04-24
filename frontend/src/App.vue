<script setup lang="ts">
import { onMounted, ref } from "vue";

import { fetchInvoices } from "./api/invoice";
import InvoiceTable from "./components/InvoiceTable.vue";
import InvoiceUpload from "./components/InvoiceUpload.vue";
import type { InvoiceRecord } from "./types/invoice";

const invoices = ref<InvoiceRecord[]>([]);

async function loadData() {
  invoices.value = await fetchInvoices();
}

onMounted(loadData);
</script>

<template>
  <main class="min-h-screen px-6 py-12">
    <div class="mx-auto max-w-6xl">
      <header class="mb-10">
        <h1 class="text-3xl font-bold tracking-tight text-slate-800">企业自动化发票报销系统</h1>
        <p class="mt-2 text-slate-500">上传 PDF 发票，自动抽取并同步到会计汇总列表。</p>
      </header>

      <InvoiceUpload @uploaded="loadData" />
      <InvoiceTable :data="invoices" />
    </div>
  </main>
</template>
