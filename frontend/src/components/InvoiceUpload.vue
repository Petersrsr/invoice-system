<script setup lang="ts">
import { ref } from "vue";
import { uploadInvoice } from "../api/invoice";
import type { UploadInvoiceResponse } from "../types/invoice";

// 上传成功时通知父组件，可选用于刷新列表。
const emit = defineEmits<{ (e: "uploaded", payload: UploadInvoiceResponse): void }>();

const isDragging = ref(false);
const loading = ref(false);
const message = ref("拖拽 PDF 到这里，或点击选择文件");

function onDragOver() {
  isDragging.value = true;
}

function onDragLeave() {
  isDragging.value = false;
}

async function handleFile(file: File) {
  // 仅允许 PDF，避免后端不必要的解析失败。
  if (!file || file.type !== "application/pdf") {
    message.value = "仅支持 PDF 文件";
    return;
  }
  loading.value = true;
  message.value = "正在上传并解析，请稍候...";
  try {
    const result = await uploadInvoice(file);
    // 覆盖旧发票时给出更强提示，避免员工误解为新建记录。
    if (result?.replaced) {
      message.value = "重复发票号：已覆盖旧文件并更新记录";
      window.alert(result?.message ?? "检测到重复发票号，已覆盖旧文件并更新记录");
    } else {
      message.value = result?.message ?? "上传成功，已完成解析";
    }
    emit("uploaded", result);
  } catch (err) {
    message.value = "上传失败，请检查后端服务或 API Key 配置";
  } finally {
    loading.value = false;
    isDragging.value = false;
  }
}

function onDrop(e: DragEvent) {
  e.preventDefault();
  // 拖拽模式只取第一个文件。
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
    <label
      class="relative flex h-[360px] w-full cursor-pointer items-center justify-center rounded-3xl border-2 border-dashed transition"
      :class="isDragging ? 'border-indigo-500 bg-indigo-50' : 'border-slate-300 bg-white'"
      @dragover.prevent="onDragOver"
      @dragleave.prevent="onDragLeave"
      @drop="onDrop"
    >
      <input type="file" accept="application/pdf" class="hidden" @change="onFileChange" />
      <div class="text-center px-8">
        <p class="text-2xl font-semibold text-slate-700">发票上传</p>
        <p class="mt-4 text-slate-500">{{ message }}</p>
        <p v-if="loading" class="mt-3 text-sm text-indigo-600">解析中...</p>
      </div>
    </label>
  </section>
</template>
