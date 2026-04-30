// 上传成功后后端返回的抽取字段结构。
export interface InvoiceExtracted {
  amount: number | null;
  date: string | null;
  seller_name: string | null;
  purpose: string | null;
  invoice_number: string | null;
  title: string | null;
  tax_id: string | null;
  item_name: string | null;
}

// 上传接口响应：包含记录 ID、归档文件名与覆盖标记。
export interface UploadInvoiceResponse {
  id: number;
  file_name: string;
  uploader_name: string | null;
  replaced: boolean;
  message: string | null;
  extracted: InvoiceExtracted;
}

// 会计列表页面使用的行数据结构。
export interface InvoiceRecord {
  id: number;
  file_name: string;
  uploader_name: string | null;
  amount: number | null;
  invoice_date: string | null;
  seller_name: string | null;
  purpose: string | null;
  invoice_number: string | null;
  title: string | null;
  tax_id: string | null;
  item_name: string | null;
  created_at: string;
  approval_status: "draft" | "pending" | "approved" | "rejected";
}

// 发票详情结构：含文件链接、预览图与原始文本。
export interface InvoiceDetail {
  id: number;
  file_name: string;
  uploader_name: string | null;
  amount: number | null;
  invoice_date: string | null;
  seller_name: string | null;
  purpose: string | null;
  invoice_number: string | null;
  tax_id: string | null;
  source_file_name: string | null;
  archived_file_name: string | null;
  source_file_url: string | null;
  archived_file_url: string | null;
  source_preview_image_url: string | null;
  archive_preview_image_url: string | null;
  preview_image_url: string | null;
  raw_text: string | null;
  created_at: string;
  approval_status: "draft" | "pending" | "approved" | "rejected";
  approval_comment: string | null;
  approver_name: string | null;
  approved_at: string | null;
}
