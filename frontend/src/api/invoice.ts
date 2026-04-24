import axios from "axios";
import type { InvoiceDetail, InvoiceRecord, UploadInvoiceResponse } from "../types/invoice";

const apiBase = (import.meta.env.VITE_API_BASE as string | undefined) ?? "http://127.0.0.1:8000/api";

const http = axios.create({
  baseURL: apiBase,
});

export async function uploadInvoice(file: File): Promise<UploadInvoiceResponse> {
  const form = new FormData();
  form.append("file", file);
  const resp = await http.post("/invoices/upload", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return resp.data;
}

export async function fetchInvoices(): Promise<InvoiceRecord[]> {
  const resp = await http.get("/invoices");
  return resp.data;
}

export async function fetchInvoiceDetail(id: number): Promise<InvoiceDetail> {
  const resp = await http.get(`/invoices/${id}`);
  return resp.data;
}
