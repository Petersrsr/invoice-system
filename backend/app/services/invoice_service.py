from sqlalchemy.orm import Session

from app.db.models import InvoiceRecord


def save_invoice(db: Session, file_name: str, raw_text: str, extracted: dict) -> InvoiceRecord:
    record = InvoiceRecord(
        file_name=file_name,
        amount=_to_float(extracted.get("amount")),
        invoice_date=extracted.get("date"),
        title=extracted.get("title"),
        tax_id=extracted.get("tax_id"),
        item_name=extracted.get("item_name"),
        raw_text=raw_text,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def list_invoices(db: Session) -> list[InvoiceRecord]:
    return db.query(InvoiceRecord).order_by(InvoiceRecord.id.desc()).all()


def _to_float(value):
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
