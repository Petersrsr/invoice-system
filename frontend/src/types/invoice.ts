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

export interface UploadInvoiceResponse {
  id: number;
  file_name: string;
  replaced: boolean;
  message: string | null;
  extracted: InvoiceExtracted;
}

export interface InvoiceRecord {
  id: number;
  file_name: string;
  amount: number | null;
  invoice_date: string | null;
  seller_name: string | null;
  purpose: string | null;
  invoice_number: string | null;
  title: string | null;
  tax_id: string | null;
  item_name: string | null;
  created_at: string;
}

export interface InvoiceDetail {
  id: number;
  file_name: string;
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
}
