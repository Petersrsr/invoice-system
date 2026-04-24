<script setup lang="ts">
import type { InvoiceRecord } from "../types/invoice";

defineProps<{ data: InvoiceRecord[] }>();
</script>

<template>
  <section class="mt-10">
    <h2 class="mb-4 text-lg font-semibold text-slate-700">会计汇总列表</h2>
    <div class="overflow-x-auto rounded-2xl border border-slate-200 bg-white">
      <table class="min-w-full text-sm">
        <thead class="bg-slate-100 text-slate-600">
          <tr>
            <th class="px-4 py-3 text-left">文件名</th>
            <th class="px-4 py-3 text-left">销售方名称</th>
            <th class="px-4 py-3 text-left">用途</th>
            <th class="px-4 py-3 text-left">金额</th>
            <th class="px-4 py-3 text-left">日期</th>
            <th class="px-4 py-3 text-left">发票号码</th>
            <th class="px-4 py-3 text-left">税号</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in data" :key="row.id" class="border-t border-slate-100">
            <td class="px-4 py-3">{{ row.file_name }}</td>
            <td class="px-4 py-3">{{ row.seller_name ?? row.title ?? "-" }}</td>
            <td class="px-4 py-3">{{ row.purpose ?? row.item_name ?? "-" }}</td>
            <td class="px-4 py-3">{{ row.amount ?? '-' }}</td>
            <td class="px-4 py-3">{{ row.invoice_date ?? '-' }}</td>
            <td class="px-4 py-3">{{ row.invoice_number ?? "-" }}</td>
            <td class="px-4 py-3">{{ row.tax_id ?? '-' }}</td>
          </tr>
          <tr v-if="data.length === 0">
            <td class="px-4 py-6 text-center text-slate-400" colspan="7">暂无解析记录</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>
