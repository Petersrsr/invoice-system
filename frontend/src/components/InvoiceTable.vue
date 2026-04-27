<script setup lang="ts">
import { ref } from "vue";
import { deleteInvoice } from "../api/invoice";
import type { InvoiceRecord } from "../types/invoice";

defineProps<{ data: InvoiceRecord[] }>();
const emit = defineEmits<{ (e: "select", id: number): void; (e: "delete"): void }>();

const deletingId = ref<number | null>(null);
const confirmDeleteId = ref<number | null>(null);

async function handleDelete(id: number) {
  if (!confirm("确定要删除这条发票记录吗？此操作不可撤销，所有相关文件将被彻底删除。")) {
    return;
  }
  
  deletingId.value = id;
  try {
    await deleteInvoice(id);
    emit("delete");
  } catch (err) {
    alert("删除失败，请重试");
  } finally {
    deletingId.value = null;
    confirmDeleteId.value = null;
  }
}
</script>

<template>
  <section>
    <h2 class="mb-4 text-lg font-semibold text-slate-700">会计汇总列表</h2>
    <div class="overflow-x-auto rounded-2xl border border-slate-200 bg-white">
      <table class="min-w-full text-sm whitespace-nowrap">
        <thead class="bg-slate-100 text-slate-600">
          <tr>
            <th class="px-4 py-3 text-left">上传人</th>
            <th class="px-4 py-3 text-left min-w-[250px]">文件名</th>
            <th class="px-4 py-3 text-left min-w-[160px]">销售方名称</th>
            <th class="px-4 py-3 text-left">用途</th>
            <th class="px-4 py-3 text-right">金额</th>
            <th class="px-4 py-3 text-center">日期</th>
            <th class="px-4 py-3 text-left min-w-[160px]">发票号码</th>
            <th class="px-4 py-3 text-left">税号</th>
            <th class="px-4 py-3 text-center">审批状态</th>
            <th class="px-4 py-3 text-center">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="row in data"
            :key="row.id"
            class="border-t border-slate-100 cursor-pointer hover:bg-slate-50 transition-colors"
            @click="emit('select', row.id)"
          >
            <td class="px-4 py-3">{{ row.uploader_name ?? "-" }}</td>
            <td class="px-4 py-3 truncate" :title="row.file_name">{{ row.file_name }}</td>
            <td class="px-4 py-3 truncate" :title="row.seller_name ?? row.title">{{ row.seller_name ?? row.title ?? "-" }}</td>
            <td class="px-4 py-3">{{ row.purpose ?? row.item_name ?? "-" }}</td>
            <td class="px-4 py-3 text-right">{{ row.amount ?? '-' }}</td>
            <td class="px-4 py-3 text-center">{{ row.invoice_date ?? '-' }}</td>
            <td class="px-4 py-3 font-mono truncate" :title="row.invoice_number">{{ row.invoice_number ?? "-" }}</td>
            <td class="px-4 py-3 font-mono truncate" :title="row.tax_id">{{ row.tax_id ?? '-' }}</td>
            <td class="px-4 py-3">
              <span
                class="inline-flex items-center justify-center rounded px-2 py-0.5 text-xs font-medium"
                :class="{
                  'bg-yellow-100 text-yellow-700': row.approval_status === 'pending',
                  'bg-green-100 text-green-700': row.approval_status === 'approved',
                  'bg-red-100 text-red-700': row.approval_status === 'rejected',
                }"
              >
                {{ row.approval_status === 'pending' ? '待审批' : row.approval_status === 'approved' ? '已批准' : '已拒绝' }}
              </span>
            </td>
            <td class="px-4 py-3">
              <button
                class="flex items-center justify-center rounded-lg p-2 text-slate-500 hover:bg-red-50 hover:text-red-600 transition-colors"
                @click.stop="handleDelete(row.id)"
                :disabled="deletingId === row.id"
                title="删除发票"
              >
                <svg v-if="deletingId !== row.id" class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                </svg>
                <svg v-else class="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              </button>
            </td>
          </tr>
          <tr v-if="data.length === 0">
            <td class="px-4 py-6 text-center text-slate-400" colspan="10">暂无解析记录</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>