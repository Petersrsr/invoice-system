<script setup lang="ts">
import { ref } from "vue";

import InvoiceUpload from "../components/InvoiceUpload.vue";
import type { UploadInvoiceResponse } from "../types/invoice";

// 员工页只保留上传入口，不展示会计数据。
const confirmOpen = ref(false);
const latestUpload = ref<UploadInvoiceResponse | null>(null);

function onUploaded(payload: UploadInvoiceResponse) {
  latestUpload.value = payload;
  confirmOpen.value = true;
}

function closeConfirm() {
  confirmOpen.value = false;
}
</script>

<template>
  <section class="rounded-2xl bg-white p-6 shadow-sm">
    <h2 class="mb-2 text-xl font-semibold text-slate-800">员工发票上传</h2>
    <p class="mb-6 text-sm text-slate-500">本页面仅提供上传能力，上传后会自动进入后台汇总。</p>
    <InvoiceUpload @uploaded="onUploaded" />

    <div v-if="confirmOpen && latestUpload" class="fixed inset-0 z-50 bg-black/30 p-4" @click.self="closeConfirm">
      <div class="mx-auto mt-16 w-full max-w-2xl rounded-2xl bg-white p-6 shadow-xl">
        <h3 class="text-lg font-semibold text-slate-800">请确认发票识别结果</h3>
        <p class="mt-1 text-sm text-slate-500">上传已完成，请员工确认以下信息是否合理。</p>

        <div class="mt-5 grid grid-cols-2 gap-3 rounded-xl bg-slate-50 p-4 text-sm">
          <p><span class="text-slate-500">记录 ID：</span>{{ latestUpload.id }}</p>
          <p><span class="text-slate-500">归档文件：</span>{{ latestUpload.file_name }}</p>
          <p><span class="text-slate-500">销售方：</span>{{ latestUpload.extracted.seller_name ?? "-" }}</p>
          <p><span class="text-slate-500">用途：</span>{{ latestUpload.extracted.purpose ?? "-" }}</p>
          <p><span class="text-slate-500">金额：</span>{{ latestUpload.extracted.amount ?? "-" }}</p>
          <p><span class="text-slate-500">日期：</span>{{ latestUpload.extracted.date ?? "-" }}</p>
          <p><span class="text-slate-500">发票号码：</span>{{ latestUpload.extracted.invoice_number ?? "-" }}</p>
          <p><span class="text-slate-500">税号：</span>{{ latestUpload.extracted.tax_id ?? "-" }}</p>
          <p class="col-span-2">
            <span class="text-slate-500">系统提示：</span>{{ latestUpload.message ?? "上传成功，已完成解析" }}
          </p>
        </div>

        <div class="mt-5 flex justify-end gap-2">
          <button
            class="rounded-lg border border-slate-300 px-4 py-2 text-sm text-slate-700 hover:bg-slate-100"
            @click="closeConfirm"
          >
            我再看一下
          </button>
          <button
            class="rounded-lg bg-indigo-600 px-4 py-2 text-sm text-white hover:bg-indigo-700"
            @click="closeConfirm"
          >
            确认无误
          </button>
        </div>
      </div>
    </div>
  </section>
</template>
