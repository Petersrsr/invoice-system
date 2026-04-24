import re
from pathlib import Path
from hashlib import md5

from sqlalchemy.orm import Session

from app.db.models import InvoiceRecord


def save_invoice(db: Session, file_name: str, raw_text: str, extracted: dict) -> InvoiceRecord:
    record = InvoiceRecord(
        file_name=file_name,
        amount=_to_float(extracted.get("amount")),
        invoice_date=extracted.get("date"),
        title=extracted.get("seller_name"),
        tax_id=extracted.get("tax_id"),
        item_name=extracted.get("purpose"),
        raw_text=raw_text,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def list_invoices(db: Session) -> list[InvoiceRecord]:
    return db.query(InvoiceRecord).order_by(InvoiceRecord.id.desc()).all()


def normalize_extracted_fields(raw_text: str, extracted: dict | None) -> dict:
    data = dict(extracted or {})
    data.setdefault("seller_name", data.get("title"))
    data.setdefault("purpose", data.get("item_name"))

    data["seller_name"] = data.get("seller_name") or _capture(raw_text, [r"销售方名称[：:\s]*([^\n]+)", r"销售方[：:\s]*([^\n]+)"])
    data["purpose"] = data.get("purpose") or _capture(raw_text, [r"项目名称[：:\s]*([^\n]+)", r"用途[：:\s]*([^\n]+)", r"品名[：:\s]*([^\n]+)"])
    data["invoice_number"] = data.get("invoice_number") or _capture(raw_text, [r"发票号码[：:\s]*([A-Za-z0-9-]{8,})", r"发票号[：:\s]*([A-Za-z0-9-]{8,})"])
    data["tax_id"] = data.get("tax_id") or _capture(raw_text, [r"税号[：:\s]*([A-Za-z0-9]{8,})"])
    data["date"] = data.get("date") or _capture(raw_text, [r"(\d{4}-\d{2}-\d{2})", r"(\d{4}/\d{2}/\d{2})"])
    data["amount"] = data.get("amount") or _capture(raw_text, [r"金额[：:\s¥￥]*([0-9]+(?:\.[0-9]{1,2})?)", r"价税合计[：:\s¥￥]*([0-9]+(?:\.[0-9]{1,2})?)"])
    return data


def build_archive_filename(extracted: dict, company_prefix: str = "矢吉") -> str:
    seller_name = _sanitize_filename_part(extracted.get("seller_name"), max_bytes=54) or "未知销售方"
    purpose = _sanitize_filename_part(extracted.get("purpose"), max_bytes=72) or "未分类"
    amount_text = _format_amount(extracted.get("amount"))
    invoice_number = _sanitize_filename_part(extracted.get("invoice_number")) or "未知号码"
    base = f"{company_prefix}-{seller_name}-{purpose}-{amount_text}元-{invoice_number}"
    if _utf8_len(base) > 220:
        # Keep deterministic uniqueness while staying under filesystem limits.
        short_hash = md5(base.encode("utf-8")).hexdigest()[:8]
        purpose = _truncate_utf8(purpose, 36)
        base = f"{company_prefix}-{seller_name}-{purpose}-{amount_text}元-{invoice_number}-{short_hash}"
    return f"{base}.pdf"


def archive_pdf(pdf_bytes: bytes, file_name: str, archive_dir: str) -> str:
    archive_path = Path(archive_dir)
    archive_path.mkdir(parents=True, exist_ok=True)
    final_name = _make_unique_file_name(archive_path, file_name)
    (archive_path / final_name).write_bytes(pdf_bytes)
    return final_name


def extract_invoice_number_from_file_name(file_name: str) -> str | None:
    match = re.match(r"^矢吉-.+-.+-.+元-(.+?)(?:-\d+)?\.pdf$", file_name)
    if not match:
        return None
    return match.group(1)


def _to_float(value):
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _sanitize_filename_part(value, max_bytes: int = 120) -> str:
    text = "" if value is None else str(value).strip()
    if not text:
        return ""
    text = re.sub(r"[\\/:*?\"<>|]", "_", text)
    text = re.sub(r"\s+", "", text)
    text = _truncate_utf8(text, max_bytes)
    return text


def _format_amount(value) -> str:
    amount = _to_float(value)
    if amount is None:
        return "0.00"
    return f"{amount:.2f}"


def _make_unique_file_name(folder: Path, file_name: str) -> str:
    target = folder / file_name
    if not target.exists():
        return file_name
    stem = target.stem
    suffix = target.suffix
    index = 2
    while True:
        candidate = f"{stem}-{index}{suffix}"
        if not (folder / candidate).exists():
            return candidate
        index += 1


def _capture(text: str, patterns: list[str]) -> str | None:
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
    return None


def _truncate_utf8(text: str, max_bytes: int) -> str:
    raw = text.encode("utf-8")
    if len(raw) <= max_bytes:
        return text
    truncated = raw[:max_bytes]
    while truncated:
        try:
            return truncated.decode("utf-8")
        except UnicodeDecodeError:
            truncated = truncated[:-1]
    return ""


def _utf8_len(text: str) -> int:
    return len(text.encode("utf-8"))
