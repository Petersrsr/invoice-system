import axios from "axios";
import type { InvoiceRecord } from "../types/invoice";

const http = axios.create({
  baseURL: "http://127.0.0.1:8000/api",
});

export async function uploadInvoice(file: File) {
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
