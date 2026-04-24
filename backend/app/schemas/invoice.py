from pydantic import BaseModel, ConfigDict


class InvoiceExtractedData(BaseModel):
    amount: float | None = None
    date: str | None = None
    title: str | None = None
    tax_id: str | None = None
    item_name: str | None = None


class InvoiceCreateResponse(BaseModel):
    id: int
    file_name: str
    extracted: InvoiceExtractedData


class InvoiceListItem(BaseModel):
    id: int
    file_name: str
    amount: float | None
    invoice_date: str | None
    title: str | None
    tax_id: str | None
    item_name: str | None
    created_at: str

    model_config = ConfigDict(from_attributes=True)
