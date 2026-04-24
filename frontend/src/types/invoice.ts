export interface InvoiceExtracted {
  amount: number | null;
  date: string | null;
  title: string | null;
  tax_id: string | null;
  item_name: string | null;
}

export interface InvoiceRecord {
  id: number;
  file_name: string;
  amount: number | null;
  invoice_date: string | null;
  title: string | null;
  tax_id: string | null;
  item_name: string | null;
  created_at: string;
}
