import json
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.config import settings
from app.schemas.invoice import (
    ApprovalRequest,
    ApprovalResponse,
    InvoiceCreateResponse,
    InvoiceDetailResponse,
    InvoiceExtractedData,
    InvoiceListItem,
)
from app.services.invoice_service import (
    archive_pdf,
    build_archive_filename,
    extract_invoice_number_from_file_name,
    find_invoice_by_number,
    get_invoice_by_id,
    list_invoices,
    normalize_extracted_fields,
    overwrite_pdf,
    save_invoice_with_files,
    save_source_pdf,
    update_invoice_with_files,
)
from app.services.llm_client import parse_invoice_with_llm
from app.services.pdf_parser import extract_text_from_pdf, render_pdf_first_page_to_png

router = APIRouter()


@router.post("/upload", response_model=InvoiceCreateResponse)
async def upload_invoice(
    file: UploadFile = File(...),
    uploader_name: str = Form(...),
    draft: bool = Form(False),
    db: Session = Depends(get_db),
):
    uploader_name = uploader_name.strip()
    if not uploader_name:
        raise HTTPException(status_code=400, detail="上传人姓名不能为空")

    if file.content_type not in {"application/pdf", "application/x-pdf"}:
        raise HTTPException(status_code=400, detail="仅支持 PDF 文件")

    pdf_bytes = await file.read()
    if not pdf_bytes:
        raise HTTPException(status_code=400, detail="上传文件为空")

    raw_text = extract_text_from_pdf(pdf_bytes)
    extracted = await parse_invoice_with_llm(raw_text)
    extracted = normalize_extracted_fields(raw_text, extracted)
    
    replaced = False
    duplicate = None
    if not draft:
        duplicate = find_invoice_by_number(db, extracted.get("invoice_number"))
        replaced = duplicate is not None
    
    if duplicate and not draft:
        source_name = overwrite_pdf(
            pdf_bytes,
            duplicate.source_file_name or (file.filename or "unknown.pdf"),
            settings.source_dir,
        )
        archive_name = overwrite_pdf(
            pdf_bytes,
            duplicate.archived_file_name or build_archive_filename(extracted, company_prefix="矢吉"),
            settings.archive_dir,
        )
        record = update_invoice_with_files(
            db,
            duplicate,
            file_name=archive_name,
            source_file_name=source_name,
            archived_file_name=archive_name,
            uploader_name=uploader_name,
            raw_text=raw_text,
            extracted=extracted,
        )
    else:
        source_name = save_source_pdf(pdf_bytes, file.filename or "unknown.pdf", settings.source_dir)
        archive_name = build_archive_filename(extracted, company_prefix="矢吉")
        archive_name = archive_pdf(pdf_bytes, archive_name, settings.archive_dir)
        record = save_invoice_with_files(
            db,
            file_name=archive_name,
            source_file_name=source_name,
            archived_file_name=archive_name,
            uploader_name=uploader_name,
            raw_text=raw_text,
            extracted=extracted,
        )

    source_preview_name = f"{record.id}-source.png"
    archive_preview_name = f"{record.id}-archive.png"
    source_preview_path = str(Path(settings.preview_dir) / source_preview_name)
    archive_preview_path = str(Path(settings.preview_dir) / archive_preview_name)
    
    try:
        render_pdf_first_page_to_png(pdf_bytes, source_preview_path)
        render_pdf_first_page_to_png(pdf_bytes, archive_preview_path)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"预览图生成失败: {str(e)}")
    
    _write_meta(
        record.id,
        {
            "source_preview_image_name": source_preview_name,
            "archive_preview_image_name": archive_preview_name,
            # Backward compatibility for older frontend payloads.
            "preview_image_name": archive_preview_name,
        },
    )

    return InvoiceCreateResponse(
        id=record.id,
        file_name=record.file_name,
        uploader_name=record.uploader_name,
        replaced=replaced,
        message="检测到重复发票号，已覆盖旧文件并更新记录" if replaced else "上传成功，已完成解析",
        extracted=InvoiceExtractedData(
            amount=record.amount,
            date=record.invoice_date,
            seller_name=record.title,
            purpose=record.item_name,
            invoice_number=record.invoice_number or extract_invoice_number_from_file_name(record.file_name),
            tax_id=record.tax_id,
            title=record.title,
            item_name=record.item_name,
        ),
    )


@router.get("", response_model=list[InvoiceListItem])
def get_all_invoices(db: Session = Depends(get_db)):
    # 按 id 倒序输出，最近上传优先展示。
    records = list_invoices(db)
    return [
        InvoiceListItem(
            id=r.id,
            file_name=r.file_name,
            uploader_name=r.uploader_name,
            amount=r.amount,
            invoice_date=r.invoice_date,
            seller_name=r.title,
            purpose=r.item_name,
            invoice_number=r.invoice_number or extract_invoice_number_from_file_name(r.file_name),
            title=r.title,
            tax_id=r.tax_id,
            item_name=r.item_name,
            created_at=r.created_at.isoformat() if hasattr(r.created_at, "isoformat") else str(r.created_at),
            approval_status=getattr(r, "approval_status", "pending"),
        )
        for r in records
    ]


@router.get("/{invoice_id}", response_model=InvoiceDetailResponse)
def get_invoice_detail(invoice_id: int, db: Session = Depends(get_db)):
    target = get_invoice_by_id(db, invoice_id)
    if not target:
        raise HTTPException(status_code=404, detail="发票记录不存在")

    return InvoiceDetailResponse(
        id=target.id,
        file_name=target.file_name,
        uploader_name=target.uploader_name,
        amount=target.amount,
        invoice_date=target.invoice_date,
        seller_name=target.title,
        purpose=target.item_name,
        invoice_number=target.invoice_number or extract_invoice_number_from_file_name(target.file_name),
        tax_id=target.tax_id,
        raw_text=target.raw_text,
        source_file_name=target.source_file_name,
        archived_file_name=target.archived_file_name,
        source_file_url=f"/files/source/{target.source_file_name}" if target.source_file_name else None,
        archived_file_url=f"/files/archive/{target.archived_file_name}" if target.archived_file_name else None,
        source_preview_image_url=_preview_url_by_id(target.id, "source_preview_image_name"),
        archive_preview_image_url=_preview_url_by_id(target.id, "archive_preview_image_name"),
        preview_image_url=_preview_url_by_id(target.id, "preview_image_name"),
        created_at=target.created_at.isoformat() if hasattr(target.created_at, "isoformat") else str(target.created_at),
        approval_status=getattr(target, "approval_status", "pending"),
        approval_comment=getattr(target, "approval_comment", None),
        approver_name=getattr(target, "approver_name", None),
        approved_at=target.approved_at.isoformat() if hasattr(target, "approved_at") and target.approved_at else None,
    )


def _write_meta(invoice_id: int, payload: dict) -> None:
    # 预览元信息用于详情页映射 source/archive 的图片文件名。
    meta_dir = Path(settings.meta_dir)
    meta_dir.mkdir(parents=True, exist_ok=True)
    meta_file = meta_dir / f"{invoice_id}.json"
    meta_file.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def _preview_url_by_id(invoice_id: int, key: str) -> str | None:
    # 从 meta 文件读取对应预览图并转换为静态资源 URL。
    meta_file = Path(settings.meta_dir) / f"{invoice_id}.json"
    if not meta_file.exists():
        return None
    try:
        data = json.loads(meta_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    preview_name = data.get(key)
    if not preview_name:
        return None
    return f"/files/preview/{preview_name}"


@router.post("/{invoice_id}/approve", response_model=ApprovalResponse)
def approve_invoice(
    invoice_id: int,
    approval: ApprovalRequest,
    db: Session = Depends(get_db),
):
    target = get_invoice_by_id(db, invoice_id)
    if not target:
        raise HTTPException(status_code=404, detail="发票记录不存在")

    if approval.status not in ("approved", "rejected"):
        raise HTTPException(status_code=400, detail="审批状态只能是 approved 或 rejected")

    if not approval.approver_name or not approval.approver_name.strip():
        raise HTTPException(status_code=400, detail="审批人姓名不能为空")

    from datetime import datetime
    target.approval_status = approval.status
    target.approval_comment = approval.comment
    target.approver_name = approval.approver_name.strip()
    target.approved_at = datetime.utcnow()
    db.commit()

    return ApprovalResponse(
        id=target.id,
        approval_status=target.approval_status,
        approval_comment=target.approval_comment,
        approver_name=target.approver_name,
        approved_at=target.approved_at.isoformat() if target.approved_at else None,
    )


@router.post("/{invoice_id}/confirm")
def confirm_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
):
    target = get_invoice_by_id(db, invoice_id)
    if not target:
        raise HTTPException(status_code=404, detail="发票记录不存在")
    
    target.approval_status = "pending"
    db.commit()
    
    return InvoiceCreateResponse(
        id=target.id,
        file_name=target.file_name,
        uploader_name=target.uploader_name,
        replaced=False,
        message="提交成功",
        extracted=InvoiceExtractedData(
            amount=target.amount,
            date=target.invoice_date,
            seller_name=target.title,
            purpose=target.item_name,
            invoice_number=target.invoice_number,
            tax_id=target.tax_id,
            title=target.title,
            item_name=target.item_name,
        ),
    )


@router.delete("/{invoice_id}/cancel")
def cancel_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
):
    target = get_invoice_by_id(db, invoice_id)
    if not target:
        raise HTTPException(status_code=404, detail="发票记录不存在")
    
    db.delete(target)
    db.commit()
    
    return {"status": "ok", "message": "已取消并删除草稿"}


@router.delete("/{invoice_id}/delete")
def delete_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
):
    target = get_invoice_by_id(db, invoice_id)
    if not target:
        raise HTTPException(status_code=404, detail="发票记录不存在")
    
    source_path = Path(settings.source_dir) / (target.source_file_name or "")
    archive_path = Path(settings.archive_dir) / (target.archived_file_name or "")
    source_preview_path = Path(settings.preview_dir) / f"{invoice_id}-source.png"
    archive_preview_path = Path(settings.preview_dir) / f"{invoice_id}-archive.png"
    meta_path = Path(settings.meta_dir) / f"{invoice_id}.json"
    
    for file_path in [source_path, archive_path, source_preview_path, archive_preview_path, meta_path]:
        if file_path.exists():
            try:
                file_path.unlink()
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"删除文件失败: {file_path} - {str(e)}")
    
    db.delete(target)
    db.commit()
    
    return {"status": "ok", "message": "已彻底删除发票记录及所有相关文件"}
