<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import { fetchInvoiceDetail, fetchInvoices } from "../api/invoice";
import InvoiceTable from "../components/InvoiceTable.vue";
import type { InvoiceDetail, InvoiceRecord } from "../types/invoice";

const invoices = ref<InvoiceRecord[]>([]);
const selected = ref<InvoiceDetail | null>(null);
const detailOpen = ref(false);
const detailLoading = ref(false);
const apiBase = (import.meta.env.VITE_API_ORIGIN as string | undefined) ?? "http://127.0.0.1:8000";

const totalAmount = computed(() =>
  invoices.value.reduce((sum, row) => sum + (row.amount ?? 0), 0),
);

const purposeStats = computed(() => {
  const bucket = new Map<string, number>();
  for (const row of invoices.value) {
    const key = row.purpose ?? "未分类";
    bucket.set(key, (bucket.get(key) ?? 0) + 1);
  }
  return [...bucket.entries()]
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count);
});

const uploaderStats = computed(() => {
  const bucket = new Map<string, number>();
  for (const row of invoices.value) {
    const key = row.uploader_name ?? "未填写";
    bucket.set(key, (bucket.get(key) ?? 0) + (row.amount ?? 0));
  }
  return [...bucket.entries()]
    .map(([name, amount]) => ({ name, amount }))
    .sort((a, b) => b.amount - a.amount)
    .slice(0, 8);
});

function purposeBarWidth(count: number): string {
  const max = purposeStats.value[0]?.count ?? 1;
  return `${Math.max((count / max) * 100, 6)}%`;
}

function uploaderBarWidth(amount: number): string {
  const max = uploaderStats.value[0]?.amount ?? 1;
  return `${Math.max((amount / max) * 100, 6)}%`;
}

// 会计页初始化时拉取汇总列表。
async function loadData() {
  invoices.value = await fetchInvoices();
}

// 点击某条记录后展示详情弹窗。
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
  <section class="rounded-2xl bg-white p-6 shadow-sm">
    <h2 class="mb-2 text-xl font-semibold text-slate-800">会计汇总管理</h2>
    <p class="text-sm text-slate-500">查看全部解析记录，支持查看源文件、归档文件与预览图。</p>

    <div class="mt-5 grid grid-cols-1 gap-4 lg:grid-cols-3">
      <div class="rounded-xl border border-slate-200 bg-slate-50 p-4">
        <p class="text-xs text-slate-500">发票总数</p>
        <p class="mt-1 text-2xl font-semibold text-slate-800">{{ invoices.length }}</p>
      </div>
      <div class="rounded-xl border border-slate-200 bg-slate-50 p-4">
        <p class="text-xs text-slate-500">金额汇总（元）</p>
        <p class="mt-1 text-2xl font-semibold text-slate-800">{{ totalAmount.toFixed(2) }}</p>
      </div>
      <div class="rounded-xl border border-slate-200 bg-slate-50 p-4">
        <p class="text-xs text-slate-500">平均每张（元）</p>
        <p class="mt-1 text-2xl font-semibold text-slate-800">
          {{ invoices.length === 0 ? "0.00" : (totalAmount / invoices.length).toFixed(2) }}
        </p>
      </div>
    </div>

    <div class="mt-4 grid grid-cols-1 gap-4 lg:grid-cols-2">
      <div class="rounded-xl border border-slate-200 p-4">
        <p class="text-sm font-medium text-slate-700">用途分布（按张数）</p>
        <div v-if="purposeStats.length === 0" class="mt-3 text-xs text-slate-400">暂无数据</div>
        <div v-else class="mt-3 space-y-2">
          <div v-for="item in purposeStats" :key="item.name">
            <div class="mb-1 flex items-center justify-between text-xs text-slate-600">
              <span>{{ item.name }}</span>
              <span>{{ item.count }} 张</span>
            </div>
            <div class="h-2 rounded bg-slate-100">
              <div class="h-2 rounded bg-indigo-500" :style="{ width: purposeBarWidth(item.count) }"></div>
            </div>
          </div>
        </div>
      </div>

      <div class="rounded-xl border border-slate-200 p-4">
        <p class="text-sm font-medium text-slate-700">上传人金额排行（Top 8）</p>
        <div v-if="uploaderStats.length === 0" class="mt-3 text-xs text-slate-400">暂无数据</div>
        <div v-else class="mt-3 space-y-2">
          <div v-for="item in uploaderStats" :key="item.name">
            <div class="mb-1 flex items-center justify-between text-xs text-slate-600">
              <span>{{ item.name }}</span>
              <span>{{ item.amount.toFixed(2) }} 元</span>
            </div>
            <div class="h-2 rounded bg-slate-100">
              <div class="h-2 rounded bg-emerald-500" :style="{ width: uploaderBarWidth(item.amount) }"></div>
            </div>
          </div>
        </div>
      </div>
    </div>

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
              <p><span class="text-slate-500">上传人：</span>{{ selected.uploader_name ?? "-" }}</p>
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
  </section>
</template>
