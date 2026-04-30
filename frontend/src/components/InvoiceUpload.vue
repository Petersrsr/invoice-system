<script setup lang="ts">
import { ref, onBeforeUnmount } from "vue";
import { uploadInvoice } from "../api/invoice";
import type { UploadInvoiceResponse } from "../types/invoice";

const emit = defineEmits<{ (e: "uploaded", payload: UploadInvoiceResponse): void }>();

const isDragging = ref(false);
const loading = ref(false);
const message = ref("拖拽 PDF 到这里，或点击选择文件");
const uploaderName = ref("");
const uploadSuccess = ref(false);
let resetTimer: ReturnType<typeof setTimeout> | null = null;

function onDragOver() {
  isDragging.value = true;
}

function onDragLeave() {
  isDragging.value = false;
}

function scheduleReset() {
  if (resetTimer !== null) clearTimeout(resetTimer);
  resetTimer = setTimeout(() => {
    uploaderName.value = "";
    uploadSuccess.value = false;
    message.value = "拖拽 PDF 到这里，或点击选择文件";
    resetTimer = null;
  }, 3000);
}

onBeforeUnmount(() => {
  if (resetTimer !== null) clearTimeout(resetTimer);
});

async function handleFile(file: File) {
  const trimmedName = uploaderName.value.trim();
  if (!trimmedName) {
    message.value = "请先填写上传人姓名";
    return;
  }
  if (!file || file.type !== "application/pdf") {
    message.value = "仅支持 PDF 文件";
    return;
  }
  if (file.size > 10 * 1024 * 1024) {
    message.value = "文件大小超过限制（最大 10MB）";
    return;
  }
  if (resetTimer !== null) {
    clearTimeout(resetTimer);
    resetTimer = null;
  }
  loading.value = true;
  uploadSuccess.value = false;
  message.value = "正在上传并解析，请稍候...";
  try {
    const result = await uploadInvoice(file, trimmedName);
    const normalizedResult: UploadInvoiceResponse = {
      ...result,
      uploader_name: result.uploader_name ?? trimmedName,
    };
    uploadSuccess.value = true;
    if (normalizedResult.replaced) {
      message.value = "重复发票号：已覆盖旧文件并更新记录";
    } else {
      message.value = "上传成功，已完成解析";
    }
    emit("uploaded", normalizedResult);
    scheduleReset();
  } catch (err) {
    uploadSuccess.value = false;
    message.value = "上传失败，请检查后端服务或 API Key 配置";
  } finally {
    loading.value = false;
    isDragging.value = false;
  }
}

function onDrop(e: DragEvent) {
  e.preventDefault();
  const file = e.dataTransfer?.files?.[0];
  if (file) {
    handleFile(file);
  }
}

function onFileChange(e: Event) {
  const target = e.target as HTMLInputElement;
  const file = target.files?.[0];
  if (file) {
    handleFile(file);
  }
}
</script>

<template>
  <section class="w-full max-w-4xl mx-auto">
    <div class="mb-4 rounded-2xl border border-slate-200 bg-white p-4">
      <label for="uploader_name" class="mb-2 block text-sm font-medium text-slate-700">上传人姓名（必填）</label>
      <input
        id="uploader_name"
        v-model="uploaderName"
        type="text"
        maxlength="50"
        placeholder="请输入姓名，例如：张三"
        class="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-indigo-500 transition-colors"
        :class="{ 'border-red-300 focus:border-red-500': !uploaderName.trim() && message === '请先填写上传人姓名' }"
      />
    </div>

    <label
      class="relative flex h-[320px] w-full cursor-pointer items-center justify-center rounded-3xl border-2 border-dashed transition-all duration-200"
      :class="isDragging ? 'border-indigo-500 bg-indigo-50 scale-[1.02] shadow-lg' : uploadSuccess ? 'border-green-500 bg-green-50' : 'border-slate-300 bg-white hover:border-indigo-300 hover:bg-slate-50'"
      @dragover.prevent="onDragOver"
      @dragleave.prevent="onDragLeave"
      @drop="onDrop"
    >
      <input type="file" accept="application/pdf" class="hidden" @change="onFileChange" />
      <div class="text-center px-8 space-y-3">
        <div class="inline-flex h-14 w-14 items-center justify-center rounded-full" :class="uploadSuccess ? 'bg-green-100' : 'bg-indigo-100'">
          <svg v-if="loading" class="h-7 w-7 animate-spin text-indigo-600" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <svg v-else-if="uploadSuccess" class="h-7 w-7 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"></path>
          </svg>
          <svg v-else class="h-7 w-7 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
          </svg>
        </div>
        <div>
          <p class="text-lg font-semibold text-slate-700">发票上传</p>
          <p class="mt-1 text-sm" :class="uploadSuccess ? 'text-green-600' : 'text-slate-500'">{{ message }}</p>
        </div>
        <p class="text-xs text-slate-400">支持 PDF 格式，最大 10MB</p>
      </div>
    </label>
  </section>
</template>
