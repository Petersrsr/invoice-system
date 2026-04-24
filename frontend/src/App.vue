<script setup lang="ts">
import { onMounted, ref } from "vue";

import { fetchInvoiceDetail, fetchInvoices } from "./api/invoice";
import InvoiceTable from "./components/InvoiceTable.vue";
import InvoiceUpload from "./components/InvoiceUpload.vue";
import type { InvoiceDetail, InvoiceRecord } from "./types/invoice";

const invoices = ref<InvoiceRecord[]>([]);
const selected = ref<InvoiceDetail | null>(null);
const detailOpen = ref(false);
const detailLoading = ref(false);

async function loadData() {
  invoices.value = await fetchInvoices();
}

async function openDetail(id: number) {
  detailLoading.value = true;
  detailOpen.value = true;
  try {
    selected.value = await fetchInvoiceDetail(id);
  } finally {
    detailLoading.value = false;
  }
}

function closeDetail() {
  detailOpen.value = false;
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
      <InvoiceTable :data="invoices" @select="openDetail" />

      <div v-if="detailOpen" class="fixed inset-0 z-50 bg-black/30 p-4" @click.self="closeDetail">
        <div class="mx-auto mt-16 max-h-[80vh] w-full max-w-4xl overflow-hidden rounded-2xl bg-white shadow-xl">
          <div class="flex items-center justify-between border-b px-5 py-4">
            <h3 class="text-lg font-semibold text-slate-800">发票详情</h3>
            <button class="rounded px-3 py-1 text-slate-500 hover:bg-slate-100" @click="closeDetail">关闭</button>
          </div>

          <div class="max-h-[calc(80vh-64px)] overflow-y-auto p-5">
            <p v-if="detailLoading" class="text-slate-500">加载中...</p>
            <div v-else-if="selected" class="space-y-4">
              <div class="grid grid-cols-2 gap-3 text-sm">
                <p><span class="text-slate-500">文件名：</span>{{ selected.file_name }}</p>
                <p><span class="text-slate-500">销售方：</span>{{ selected.seller_name ?? "-" }}</p>
                <p><span class="text-slate-500">用途：</span>{{ selected.purpose ?? "-" }}</p>
                <p><span class="text-slate-500">金额：</span>{{ selected.amount ?? "-" }}</p>
                <p><span class="text-slate-500">日期：</span>{{ selected.invoice_date ?? "-" }}</p>
                <p><span class="text-slate-500">发票号码：</span>{{ selected.invoice_number ?? "-" }}</p>
                <p><span class="text-slate-500">税号：</span>{{ selected.tax_id ?? "-" }}</p>
                <p><span class="text-slate-500">入库时间：</span>{{ selected.created_at }}</p>
              </div>

              <div>
                <p class="mb-2 text-sm font-medium text-slate-700">发票提取原文</p>
                <pre class="whitespace-pre-wrap rounded-xl bg-slate-50 p-4 text-xs text-slate-700">{{ selected.raw_text ?? "-" }}</pre>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </main>
</template>
