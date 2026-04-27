from pydantic import BaseModel, ConfigDict


# LLM 与规则兜底后的字段结构。
class InvoiceExtractedData(BaseModel):
    amount: float | None = None
    date: str | None = None
    seller_name: str | None = None
    purpose: str | None = None
    invoice_number: str | None = None
    tax_id: str | None = None
    title: str | None = None
    item_name: str | None = None


class InvoiceCreateResponse(BaseModel):
    id: int
    file_name: str
    uploader_name: str | None = None
    replaced: bool = False
    message: str | None = None
    extracted: InvoiceExtractedData


class InvoiceListItem(BaseModel):
    id: int
    file_name: str
    uploader_name: str | None
    amount: float | None
    invoice_date: str | None
    seller_name: str | None
    purpose: str | None
    invoice_number: str | None
    title: str | None
    tax_id: str | None
    item_name: str | None
    created_at: str
    approval_status: str = "pending"

    model_config = ConfigDict(from_attributes=True)


class InvoiceDetailResponse(BaseModel):
    id: int
    file_name: str
    uploader_name: str | None
    amount: float | None
    invoice_date: str | None
    seller_name: str | None
    purpose: str | None
    invoice_number: str | None
    tax_id: str | None
    source_file_name: str | None
    archived_file_name: str | None
    source_file_url: str | None
    archived_file_url: str | None
    source_preview_image_url: str | None
    archive_preview_image_url: str | None
    preview_image_url: str | None
    raw_text: str | None
    created_at: str
    approval_status: str = "pending"
    approval_comment: str | None = None
    approver_name: str | None = None
    approved_at: str | None = None


class ApprovalRequest(BaseModel):
    status: str
    comment: str | None = None
    approver_name: str


class ApprovalResponse(BaseModel):
    id: int
    approval_status: str
    approval_comment: str | None
    approver_name: str | None
    approved_at: str | None
