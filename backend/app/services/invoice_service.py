import re
from pathlib import Path
from hashlib import md5

from sqlalchemy.orm import Session

from app.db.models import InvoiceRecord

PURPOSE_KEYWORDS: dict[str, list[str]] = {
    "食品": ["餐", "食品", "饮料", "烘焙", "便利店", "外卖", "快餐", "零食", "咖啡", "面包", "牛奶"],
    "交通": ["交通", "打车", "出租车", "地铁", "公交", "高铁", "机票", "火车", "出行", "过路", "停车"],
    "住宿": ["酒店", "住宿", "旅馆", "宾馆", "民宿"],
    "办公": ["办公", "文具", "打印", "耗材", "纸", "笔", "文件夹", "工位"],
    "通信": ["通信", "电话", "宽带", "网络", "流量", "话费"],
    "培训": ["培训", "课程", "学习", "讲座", "认证"],
    "医疗": ["医疗", "医院", "药", "体检", "门诊"],
    "服务": ["服务", "咨询", "维护", "维修", "代办", "手续费"],
    "设备": ["设备", "电脑", "显示器", "硬盘", "鼠标", "键盘", "服务器"],
}


def save_invoice(db: Session, file_name: str, raw_text: str, extracted: dict) -> InvoiceRecord:
    # 兼容旧接口的保留方法（当前主流程优先使用 save_invoice_with_files）。
    record = InvoiceRecord(
        file_name=file_name,
        invoice_number=extracted.get("invoice_number"),
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


def save_invoice_with_files(
    db: Session,
    file_name: str,
    source_file_name: str,
    archived_file_name: str,
    uploader_name: str | None,
    raw_text: str,
    extracted: dict,
) -> InvoiceRecord:
    record = InvoiceRecord(
        file_name=file_name,
        source_file_name=source_file_name,
        archived_file_name=archived_file_name,
        uploader_name=uploader_name,
        invoice_number=extracted.get("invoice_number"),
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
    # 会计页面按最新记录优先查看。
    return db.query(InvoiceRecord).order_by(InvoiceRecord.id.desc()).all()


def get_invoice_by_id(db: Session, invoice_id: int) -> InvoiceRecord | None:
    return db.query(InvoiceRecord).filter(InvoiceRecord.id == invoice_id).first()


def find_invoice_by_number(db: Session, invoice_number: str | None) -> InvoiceRecord | None:
    number = _normalize_invoice_number(invoice_number)
    if not number:
        return None
    record = (
        db.query(InvoiceRecord)
        .filter(InvoiceRecord.invoice_number == number)
        .order_by(InvoiceRecord.id.desc())
        .first()
    )
    if record:
        return record
    # 兼容历史数据：若旧行没有 invoice_number，则从文件名反推出发票号。
    for item in list_invoices(db):
        if _normalize_invoice_number(extract_invoice_number_from_file_name(item.file_name)) == number:
            return item
    return None


def update_invoice_with_files(
    db: Session,
    record: InvoiceRecord,
    file_name: str,
    source_file_name: str,
    archived_file_name: str,
    uploader_name: str | None,
    raw_text: str,
    extracted: dict,
) -> InvoiceRecord:
    record.file_name = file_name
    record.source_file_name = source_file_name
    record.archived_file_name = archived_file_name
    record.uploader_name = uploader_name
    record.invoice_number = extracted.get("invoice_number")
    record.amount = _to_float(extracted.get("amount"))
    record.invoice_date = extracted.get("date")
    record.title = extracted.get("seller_name")
    record.tax_id = extracted.get("tax_id")
    record.item_name = extracted.get("purpose")
    record.raw_text = raw_text
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def normalize_extracted_fields(raw_text: str, extracted: dict | None) -> dict:
    # 先信任 LLM，再用规则补齐缺失字段。
    data = dict(extracted or {})
    data.setdefault("seller_name", data.get("title"))
    data.setdefault("purpose", data.get("item_name"))

    data["seller_name"] = data.get("seller_name") or _capture(raw_text, [r"销售方名称[：:\s]*([^\n]+)", r"销售方[：:\s]*([^\n]+)"])
    data["purpose"] = data.get("purpose") or _capture(raw_text, [r"项目名称[：:\s]*([^\n]+)", r"用途[：:\s]*([^\n]+)", r"品名[：:\s]*([^\n]+)"])
    data["invoice_number"] = data.get("invoice_number") or _capture(raw_text, [r"发票号码[：:\s]*([A-Za-z0-9-]{8,})", r"发票号[：:\s]*([A-Za-z0-9-]{8,})"])
    data["tax_id"] = data.get("tax_id") or _capture(raw_text, [r"税号[：:\s]*([A-Za-z0-9]{8,})"])
    data["date"] = data.get("date") or _capture(raw_text, [r"(\d{4}-\d{2}-\d{2})", r"(\d{4}/\d{2}/\d{2})"])
    data["amount"] = data.get("amount") or _capture(raw_text, [r"金额[：:\s¥￥]*([0-9]+(?:\.[0-9]{1,2})?)", r"价税合计[：:\s¥￥]*([0-9]+(?:\.[0-9]{1,2})?)"])
    data["purpose"] = _normalize_purpose(data.get("purpose"), raw_text)
    return data


def build_archive_filename(extracted: dict, company_prefix: str = "矢吉") -> str:
    seller_name = _sanitize_filename_part(extracted.get("seller_name"), max_bytes=54) or "未知销售方"
    purpose = _sanitize_filename_part(extracted.get("purpose"), max_bytes=72) or "未分类"
    amount_text = _format_amount(extracted.get("amount"))
    invoice_number = _sanitize_filename_part(extracted.get("invoice_number")) or "未知号码"
    base = f"{company_prefix}-{seller_name}-{purpose}-{amount_text}元-{invoice_number}"
    if _utf8_len(base) > 220:
        # 文件名过长时追加短哈希，兼顾可读性与唯一性。
        short_hash = md5(base.encode("utf-8")).hexdigest()[:8]
        purpose = _truncate_utf8(purpose, 36)
        base = f"{company_prefix}-{seller_name}-{purpose}-{amount_text}元-{invoice_number}-{short_hash}"
    return f"{base}.pdf"


def archive_pdf(pdf_bytes: bytes, file_name: str, archive_dir: str) -> str:
    archive_path = Path(archive_dir).resolve()
    archive_path.mkdir(parents=True, exist_ok=True)
    final_name = _make_unique_file_name(archive_path, file_name)
    final_path = (archive_path / final_name).resolve()
    if not str(final_path).startswith(str(archive_path)):
        raise ValueError("无效的文件路径")
    final_path.write_bytes(pdf_bytes)
    return final_name


def overwrite_pdf(pdf_bytes: bytes, file_name: str, folder: str) -> str:
    # 用于重复发票覆盖场景，文件名保持原值。
    path = Path(folder).resolve()
    safe_name = _sanitize_filename_part(file_name)
    if not safe_name.lower().endswith(".pdf"):
        safe_name = f"{safe_name}.pdf"
    final_path = (path / safe_name).resolve()
    if not str(final_path).startswith(str(path)):
        raise ValueError("无效的文件路径")
    path.mkdir(parents=True, exist_ok=True)
    final_path.write_bytes(pdf_bytes)
    return safe_name


def save_source_pdf(pdf_bytes: bytes, original_file_name: str, source_dir: str) -> str:
    # 源文件默认保留原始文件名，冲突时自动追加序号。
    source_path = Path(source_dir).resolve()
    source_path.mkdir(parents=True, exist_ok=True)
    safe_original = _sanitize_filename_part(original_file_name or "unknown.pdf")
    if not safe_original.lower().endswith(".pdf"):
        safe_original = f"{safe_original}.pdf"
    final_name = _make_unique_file_name(source_path, safe_original)
    final_path = (source_path / final_name).resolve()
    if not str(final_path).startswith(str(source_path)):
        raise ValueError("无效的文件路径")
    final_path.write_bytes(pdf_bytes)
    return final_name


def extract_invoice_number_from_file_name(file_name: str) -> str | None:
    match = re.match(r"^矢吉-.+-.+-.+元-(.+?)(?:-\d+)?\.pdf$", file_name)
    if not match:
        return None
    return match.group(1)


def _normalize_invoice_number(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = str(value).strip()
    if not cleaned or cleaned in {"未知号码", "null", "None"}:
        return None
    return cleaned


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


def _normalize_purpose(purpose: str | None, raw_text: str) -> str:
    # 用途归类同时参考 LLM 输出与原文关键词，提高稳定性。
    source = f"{purpose or ''} {raw_text}"
    source = source.lower()
    for category, keywords in PURPOSE_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in source:
                return category
    if purpose:
        return "其他"
    return "其他"
