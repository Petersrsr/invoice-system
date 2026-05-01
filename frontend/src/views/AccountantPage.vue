<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import { approveInvoice, fetchInvoiceDetail, fetchInvoices, fileBase } from "../api/invoice";
import InvoiceTable from "../components/InvoiceTable.vue";
import type { InvoiceDetail, InvoiceRecord } from "../types/invoice";

const invoices = ref<InvoiceRecord[]>([]);
const selected = ref<InvoiceDetail | null>(null);
const detailOpen = ref(false);
const detailLoading = ref(false);
const approvalLoading = ref(false);
const approvalDialogOpen = ref(false);
const approvalForm = ref({ status: "approved" as "approved" | "rejected", comment: "", approverName: "" });
const imagePreviewOpen = ref(false);
const imagePreviewSrc = ref("");
const imagePreviewAlt = ref("");

const totalAmount = computed(() =>
  invoices.value.filter(i => i.approval_status !== "draft").reduce((sum, row) => sum + (row.amount ?? 0), 0),
);

const draftCount = computed(() => invoices.value.filter(i => i.approval_status === "draft").length);
const pendingCount = computed(() => invoices.value.filter(i => i.approval_status === "pending").length);
const approvedCount = computed(() => invoices.value.filter(i => i.approval_status === "approved").length);
const rejectedCount = computed(() => invoices.value.filter(i => i.approval_status === "rejected").length);

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

function openImagePreview(src: string, alt: string) {
  imagePreviewSrc.value = src;
  imagePreviewAlt.value = alt;
  imagePreviewOpen.value = true;
}

function closeImagePreview() {
  imagePreviewOpen.value = false;
  imagePreviewSrc.value = "";
  imagePreviewAlt.value = "";
}

function purposeBarWidth(count: number): string {
  const max = purposeStats.value[0]?.count ?? 1;
  return `${Math.max((count / max) * 100, 6)}%`;
}

function uploaderBarWidth(amount: number): string {
  const max = uploaderStats.value[0]?.amount ?? 1;
  return `${Math.max((amount / max) * 100, 6)}%`;
}

async function loadData() {
  try {
    invoices.value = await fetchInvoices();
  } catch {
    // 静默处理，保留已有数据
  }
}

async function openDetail(id: number) {
  detailLoading.value = true;
  detailOpen.value = true;
  selected.value = null;
  try {
    selected.value = await fetchInvoiceDetail(id);
  } catch {
    detailOpen.value = false;
  } finally {
    detailLoading.value = false;
  }
}

function closeDetail() {
  detailOpen.value = false;
  selected.value = null;
}

function openApprovalDialog() {
  approvalForm.value = { status: "approved", comment: "", approverName: "" };
  approvalDialogOpen.value = true;
}

async function submitApproval() {
  if (!selected.value || !approvalForm.value.approverName.trim()) {
    alert("请填写审批人姓名");
    return;
  }
  approvalLoading.value = true;
  const invoiceId = selected.value.id;
  try {
    await approveInvoice(invoiceId, {
      status: approvalForm.value.status,
      comment: approvalForm.value.comment,
      approver_name: approvalForm.value.approverName.trim(),
    });
    approvalDialogOpen.value = false;
    try {
      selected.value = await fetchInvoiceDetail(invoiceId);
      await loadData();
    } catch {
      // 审批已成功，刷新失败不影响结果
    }
    alert("审批提交成功");
  } catch {
    alert("审批提交失败，请重试");
  } finally {
    approvalLoading.value = false;
  }
}

onMounted(loadData);
</script>

<template>
  <section class="space-y-4">
    <div class="rounded-2xl bg-white p-5 shadow-sm">
      <div class="flex flex-wrap items-center justify-between gap-2">
        <div>
          <h2 class="text-xl font-semibold text-slate-800">发票管理</h2>
          <p class="mt-1 text-sm text-slate-500">查看发票记录、统计分析及审批管理</p>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 gap-4 lg:grid-cols-3">
      <div class="rounded-xl border border-slate-200 bg-slate-50 p-4">
        <p class="text-xs text-slate-500">发票总数</p>
        <p class="mt-1 text-2xl font-semibold text-slate-800">{{ invoices.length }} 张</p>
      </div>
      <div class="rounded-xl border border-slate-200 bg-slate-50 p-4">
        <p class="text-xs text-slate-500">总金额</p>
        <p class="mt-1 text-2xl font-semibold text-slate-800">{{ totalAmount.toFixed(2) }} 元</p>
      </div>
      <div class="rounded-xl border border-slate-200 bg-slate-50 p-4">
        <p class="text-xs text-slate-500">草稿 / 待审批 / 已批准 / 已拒绝</p>
        <p class="mt-1 text-2xl font-semibold text-slate-800">
          <span class="text-slate-500">{{ draftCount }}</span>
          <span class="text-slate-400"> / </span>
          <span class="text-yellow-600">{{ pendingCount }}</span>
          <span class="text-slate-400"> / </span>
          <span class="text-green-600">{{ approvedCount }}</span>
          <span class="text-slate-400"> / </span>
          <span class="text-red-600">{{ rejectedCount }}</span>
        </p>
      </div>
    </div>

    <div class="grid grid-cols-1 gap-4 lg:grid-cols-2">
      <div class="rounded-xl border border-slate-200 p-4">
        <p class="text-sm font-medium text-slate-700">用途分布</p>
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
        <p class="text-sm font-medium text-slate-700">报销金额排行</p>
        <div v-if="uploaderStats.length === 0" class="mt-3 text-xs text-slate-400">暂无数据</div>
        <div v-else class="mt-3 space-y-2">
          <div v-for="(item, index) in uploaderStats" :key="item.name">
            <div class="mb-1 flex items-center justify-between text-xs text-slate-600">
              <span class="flex items-center gap-2">
                <span v-if="index < 3" class="rounded-full bg-indigo-100 px-1.5 py-0.5 text-[10px] font-medium text-indigo-600">
                  {{ index + 1 }}
                </span>
                <span v-else class="w-4"></span>
                {{ item.name }}
              </span>
              <span>{{ item.amount.toFixed(2) }} 元</span>
            </div>
            <div class="h-2 rounded bg-slate-100">
              <div class="h-2 rounded bg-emerald-500" :style="{ width: uploaderBarWidth(item.amount) }"></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="rounded-2xl bg-white p-5 shadow-sm">
      <InvoiceTable :data="invoices" @select="openDetail" @delete="loadData" />
    </div>

    <div v-if="detailOpen" class="fixed inset-0 z-50 bg-black/30 p-4" @click.self="closeDetail">
      <div class="mx-auto mt-16 max-h-[80vh] w-full max-w-4xl overflow-hidden rounded-2xl bg-white shadow-xl">
        <div class="flex items-center justify-between border-b px-5 py-4">
          <h3 class="text-lg font-semibold text-slate-800">发票详情</h3>
          <div class="flex items-center gap-2">
            <button
              v-if="selected?.approval_status === 'pending'"
              class="rounded bg-indigo-600 px-4 py-1.5 text-sm text-white hover:bg-indigo-700"
              @click="openApprovalDialog"
            >
              审批
            </button>
            <button class="rounded px-3 py-1 text-slate-500 hover:bg-slate-100" @click="closeDetail">关闭</button>
          </div>
        </div>

        <div class="max-h-[calc(80vh-64px)] overflow-y-auto p-5">
          <p v-if="detailLoading" class="text-center text-slate-500">加载中...</p>
          <div v-else-if="selected" class="space-y-4">
            <div class="grid grid-cols-2 gap-3 text-sm">
              <p><span class="text-slate-500">上传人：</span>{{ selected.uploader_name ?? "-" }}</p>
              <p><span class="text-slate-500">文件名：</span>{{ selected.file_name }}</p>
              <p><span class="text-slate-500">销售方：</span>{{ selected.seller_name ?? "-" }}</p>
              <p><span class="text-slate-500">用途：</span>{{ selected.purpose ?? "-" }}</p>
              <p><span class="text-slate-500">金额：</span>{{ selected.amount ?? "-" }} 元</p>
              <p><span class="text-slate-500">开票日期：</span>{{ selected.invoice_date ?? "-" }}</p>
              <p><span class="text-slate-500">发票号码：</span>{{ selected.invoice_number ?? "-" }}</p>
              <p><span class="text-slate-500">税号：</span>{{ selected.tax_id ?? "-" }}</p>
              <p><span class="text-slate-500">入库时间：</span>{{ selected.created_at }}</p>
              <p>
                <span class="text-slate-500">审批状态：</span>
                <span
                  class="rounded px-2 py-0.5 text-xs font-medium"
                  :class="{
                    'bg-slate-100 text-slate-600': selected.approval_status === 'draft',
                    'bg-yellow-100 text-yellow-700': selected.approval_status === 'pending',
                    'bg-green-100 text-green-700': selected.approval_status === 'approved',
                    'bg-red-100 text-red-700': selected.approval_status === 'rejected',
                  }"
                >
                  {{ selected.approval_status === 'draft' ? '草稿' : selected.approval_status === 'pending' ? '待审批' : selected.approval_status === 'approved' ? '已批准' : '已拒绝' }}
                </span>
              </p>
              <template v-if="selected.approval_status !== 'pending'">
                <p><span class="text-slate-500">审批人：</span>{{ selected.approver_name ?? '-' }}</p>
                <p><span class="text-slate-500">审批时间：</span>{{ selected.approved_at ?? '-' }}</p>
                <p v-if="selected.approval_comment"><span class="text-slate-500">审批备注：</span>{{ selected.approval_comment }}</p>
              </template>
              <p>
                <span class="text-slate-500">源文件：</span>
                <a
                  v-if="selected.source_file_url"
                  class="text-indigo-600 hover:underline"
                  :href="`${fileBase}${selected.source_file_url}`"
                  target="_blank"
                >下载</a>
                <span v-else>-</span>
              </p>
              <p>
                <span class="text-slate-500">归档文件：</span>
                <a
                  v-if="selected.archived_file_url"
                  class="text-indigo-600 hover:underline"
                  :href="`${fileBase}${selected.archived_file_url}`"
                  target="_blank"
                >下载</a>
                <span v-else>-</span>
              </p>
            </div>

            <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
              <div>
                <p class="mb-2 text-sm font-medium text-slate-700">源发票预览</p>
                <div class="rounded-xl bg-slate-50 p-3">
                  <img
                    v-if="selected.source_preview_image_url || selected.preview_image_url"
                    :src="`${fileBase}${selected.source_preview_image_url ?? selected.preview_image_url}`"
                    alt="source invoice preview"
                    class="max-h-[60vh] w-full cursor-pointer object-contain transition-transform hover:scale-[1.02]"
                    @click="openImagePreview(`${fileBase}${selected.source_preview_image_url ?? selected.preview_image_url}`, '源发票预览')"
                  />
                  <p v-else class="text-xs text-slate-500">暂无预览图</p>
                </div>
              </div>
              <div>
                <p class="mb-2 text-sm font-medium text-slate-700">归档发票预览</p>
                <div class="rounded-xl bg-slate-50 p-3">
                  <img
                    v-if="selected.archive_preview_image_url || selected.preview_image_url"
                    :src="`${fileBase}${selected.archive_preview_image_url ?? selected.preview_image_url}`"
                    alt="archived invoice preview"
                    class="max-h-[60vh] w-full cursor-pointer object-contain transition-transform hover:scale-[1.02]"
                    @click="openImagePreview(`${fileBase}${selected.archive_preview_image_url ?? selected.preview_image_url}`, '归档发票预览')"
                  />
                  <p v-else class="text-xs text-slate-500">暂无预览图</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="approvalDialogOpen" class="fixed inset-0 z-[60] bg-black/30 p-4" @click.self="!approvalLoading && (approvalDialogOpen = false)">
      <div class="mx-auto mt-24 max-w-md rounded-2xl bg-white p-6 shadow-xl">
        <h3 class="mb-4 text-lg font-semibold text-slate-800">审批操作</h3>
        <div class="space-y-4">
          <div>
            <label class="mb-1 block text-sm text-slate-600">审批结果</label>
            <div class="flex gap-4">
              <label class="flex items-center gap-2">
                <input type="radio" v-model="approvalForm.status" value="approved" />
                <span>批准通过</span>
              </label>
              <label class="flex items-center gap-2">
                <input type="radio" v-model="approvalForm.status" value="rejected" />
                <span>拒绝驳回</span>
              </label>
            </div>
          </div>
          <div>
            <label class="mb-1 block text-sm text-slate-600">审批人姓名</label>
            <input
              v-model="approvalForm.approverName"
              type="text"
              placeholder="请输入您的姓名"
              class="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-indigo-500"
            />
          </div>
          <div>
            <label class="mb-1 block text-sm text-slate-600">备注说明（可选）</label>
            <textarea
              v-model="approvalForm.comment"
              rows="3"
              placeholder="如有特殊情况，请在此说明"
              class="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-indigo-500"
            ></textarea>
          </div>
          <div class="flex justify-end gap-2">
            <button
              class="rounded px-4 py-2 text-sm text-slate-600 hover:bg-slate-100"
              @click="approvalDialogOpen = false"
            >
              取消
            </button>
            <button
              class="rounded bg-indigo-600 px-4 py-2 text-sm text-white hover:bg-indigo-700 disabled:opacity-50"
              :disabled="approvalLoading"
              @click="submitApproval"
            >
              {{ approvalLoading ? "提交中..." : "确认审批" }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="imagePreviewOpen" class="fixed inset-0 z-[70] flex items-center justify-center bg-black/80 p-4" @click.self="closeImagePreview">
      <button
        class="absolute right-4 top-4 rounded-full bg-white/20 p-2 text-white hover:bg-white/30 transition-colors"
        @click="closeImagePreview"
      >
        <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"></path>
        </svg>
      </button>
      <img
        :src="imagePreviewSrc"
        :alt="imagePreviewAlt"
        class="max-h-[90vh] max-w-[90vw] rounded-lg shadow-2xl object-contain"
      />
    </div>
  </section>
</template>