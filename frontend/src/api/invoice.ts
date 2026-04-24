import axios from "axios";
import type { InvoiceDetail, InvoiceRecord, UploadInvoiceResponse } from "../types/invoice";

// 前端统一 API 基址，默认指向本地 FastAPI 服务。
const apiBase = (import.meta.env.VITE_API_BASE as string | undefined) ?? "http://127.0.0.1:8000/api";

const http = axios.create({
  baseURL: apiBase,
});

// 上传发票 PDF，后端返回解析结果与是否覆盖信息。
export async function uploadInvoice(file: File, uploaderName: string): Promise<UploadInvoiceResponse> {
  const form = new FormData();
  form.append("file", file);
  form.append("uploader_name", uploaderName);
  const resp = await http.post("/invoices/upload", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return resp.data;
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
