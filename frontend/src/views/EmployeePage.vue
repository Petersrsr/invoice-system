<script setup lang="ts">
import { ref } from "vue";

import InvoiceUpload from "../components/InvoiceUpload.vue";
import type { UploadInvoiceResponse } from "../types/invoice";

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
  <section class="space-y-4">
    <div class="rounded-2xl bg-white p-5 shadow-sm">
      <div>
        <h2 class="text-xl font-semibold text-slate-800">发票上传</h2>
        <p class="mt-1 text-sm text-slate-500">请填写上传人姓名后上传 PDF 发票文件</p>
      </div>
    </div>

    <div class="rounded-2xl bg-white p-5 shadow-sm">
    <InvoiceUpload @uploaded="onUploaded" />
    </div>

    <div v-if="confirmOpen && latestUpload" class="fixed inset-0 z-50 bg-black/30 p-4" @click.self="closeConfirm">
      <div class="mx-auto mt-16 w-full max-w-2xl rounded-2xl bg-white p-6 shadow-xl">
        <h3 class="text-lg font-semibold text-slate-800">发票识别完成</h3>
        <p class="mt-1 text-sm text-slate-500">请确认以下识别信息是否正确</p>

        <div class="mt-5 grid grid-cols-2 gap-3 rounded-xl bg-slate-50 p-4 text-sm">
          <p><span class="text-slate-500">记录编号：</span>{{ latestUpload.id }}</p>
          <p><span class="text-slate-500">上传人：</span>{{ latestUpload.uploader_name ?? "未填写" }}</p>
          <p><span class="text-slate-500">归档名称：</span>{{ latestUpload.file_name }}</p>
          <p><span class="text-slate-500">销售方：</span>{{ latestUpload.extracted.seller_name ?? "-" }}</p>
          <p><span class="text-slate-500">用途分类：</span>{{ latestUpload.extracted.purpose ?? "-" }}</p>
          <p><span class="text-slate-500">金额：</span>{{ latestUpload.extracted.amount ?? "-" }} 元</p>
          <p><span class="text-slate-500">开票日期：</span>{{ latestUpload.extracted.date ?? "-" }}</p>
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
            返回修改
          </button>
          <button
            class="rounded-lg bg-indigo-600 px-4 py-2 text-sm text-white hover:bg-indigo-700"
            @click="closeConfirm"
          >
            确认提交
          </button>
        </div>
      </div>
    </div>
  </section>
</template>