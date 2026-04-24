from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.invoice import InvoiceCreateResponse, InvoiceExtractedData, InvoiceListItem
from app.services.invoice_service import list_invoices, save_invoice
from app.services.llm_client import parse_invoice_with_llm
from app.services.pdf_parser import extract_text_from_pdf

router = APIRouter()


@router.post("/upload", response_model=InvoiceCreateResponse)
async def upload_invoice(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if file.content_type not in {"application/pdf", "application/x-pdf"}:
        raise HTTPException(status_code=400, detail="仅支持 PDF 文件")

    pdf_bytes = await file.read()
    if not pdf_bytes:
        raise HTTPException(status_code=400, detail="上传文件为空")

    raw_text = extract_text_from_pdf(pdf_bytes)
    extracted = await parse_invoice_with_llm(raw_text)
    record = save_invoice(db, file.filename or "unknown.pdf", raw_text, extracted)

    return InvoiceCreateResponse(
        id=record.id,
        file_name=record.file_name,
        extracted=InvoiceExtractedData(
            amount=record.amount,
            date=record.invoice_date,
            title=record.title,
            tax_id=record.tax_id,
            item_name=record.item_name,
        ),
    )


@router.get("", response_model=list[InvoiceListItem])
def get_all_invoices(db: Session = Depends(get_db)):
    records = list_invoices(db)
    return [
        InvoiceListItem(
            id=r.id,
            file_name=r.file_name,
            amount=r.amount,
            invoice_date=r.invoice_date,
            title=r.title,
            tax_id=r.tax_id,
            item_name=r.item_name,
            created_at=r.created_at.isoformat() if hasattr(r.created_at, "isoformat") else str(r.created_at),
        )
        for r in records
    ]
