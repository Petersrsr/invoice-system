import axios from "axios";
import type { InvoiceDetail, InvoiceRecord, UploadInvoiceResponse } from "../types/invoice";

export interface ApprovalRequest {
  status: "approved" | "rejected";
  comment?: string;
  approver_name: string;
}

export interface ApprovalResponse {
  id: number;
  approval_status: string;
  approval_comment: string | null;
  approver_name: string | null;
  approved_at: string | null;
}

// 默认跟随当前访问主机，避免局域网访问时落到访问者本机的 127.0.0.1。
const defaultApiBase = `${window.location.protocol}//${window.location.hostname}:8000/api`;
const apiBase = (import.meta.env.VITE_API_BASE as string | undefined) ?? defaultApiBase;

const http = axios.create({
  baseURL: apiBase,
});

// 上传发票 PDF，后端返回解析结果与是否覆盖信息。
export async function uploadInvoice(file: File, uploaderName: string, draft: boolean = true): Promise<UploadInvoiceResponse> {
  const form = new FormData();
  form.append("file", file);
  form.append("uploader_name", uploaderName);
  form.append("draft", String(draft));
  const resp = await http.post("/invoices/upload", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return resp.data;
}

// 确认提交草稿
export async function confirmInvoice(id: number): Promise<UploadInvoiceResponse> {
  const resp = await http.post(`/invoices/${id}/confirm`);
  return resp.data;
}

// 取消并删除草稿
export async function cancelInvoice(id: number): Promise<void> {
  await http.delete(`/invoices/${id}/cancel`);
}

// 拉取会计汇总列表。
export async function fetchInvoices(): Promise<InvoiceRecord[]> {
  const resp = await http.get("/invoices");
  return resp.data;
}

// 拉取单条发票详情，用于弹窗展示。
export async function fetchInvoiceDetail(id: number): Promise<InvoiceDetail> {
  const resp = await http.get(`/invoices/${id}`);
  return resp.data;
}

// 审批发票（批准或拒绝）。
export async function approveInvoice(id: number, approval: ApprovalRequest): Promise<ApprovalResponse> {
  const resp = await http.post(`/invoices/${id}/approve`, approval);
  return resp.data;
}

// 删除发票（彻底删除）
export async function deleteInvoice(id: number): Promise<void> {
  await http.delete(`/invoices/${id}/delete`);
}
