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
const apiBase = (import.meta.env.VITE_API_ORIGIN as string | undefined) ?? "http://127.0.0.1:8000";

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
                <p>
                  <span class="text-slate-500">源文件：</span>
                  <a
                    v-if="selected.source_file_url"
                    class="text-indigo-600 hover:underline"
                    :href="`${apiBase}${selected.source_file_url}`"
                    target="_blank"
                  >下载查看</a>
                  <span v-else>-</span>
                </p>
                <p>
                  <span class="text-slate-500">归档文件：</span>
                  <a
                    v-if="selected.archived_file_url"
                    class="text-indigo-600 hover:underline"
                    :href="`${apiBase}${selected.archived_file_url}`"
                    target="_blank"
                  >下载查看</a>
                  <span v-else>-</span>
                </p>
              </div>

              <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
                <div>
                  <p class="mb-2 text-sm font-medium text-slate-700">源发票预览（首张）</p>
                  <div class="rounded-xl bg-slate-50 p-3">
                    <img
                      v-if="selected.source_preview_image_url || selected.preview_image_url"
                      :src="`${apiBase}${selected.source_preview_image_url ?? selected.preview_image_url}`"
                      alt="source invoice preview"
                      class="max-h-[60vh] w-full object-contain"
                    />
                    <p v-else class="text-xs text-slate-500">暂无源发票预览图</p>
                  </div>
                </div>
                <div>
                  <p class="mb-2 text-sm font-medium text-slate-700">归档发票预览（首张）</p>
                  <div class="rounded-xl bg-slate-50 p-3">
                    <img
                      v-if="selected.archive_preview_image_url || selected.preview_image_url"
                      :src="`${apiBase}${selected.archive_preview_image_url ?? selected.preview_image_url}`"
                      alt="archived invoice preview"
                      class="max-h-[60vh] w-full object-contain"
                    />
                    <p v-else class="text-xs text-slate-500">暂无归档发票预览图</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </main>
</template>
