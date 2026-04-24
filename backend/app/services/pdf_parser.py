import fitz
from pathlib import Path


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    # 提取整份 PDF 的可读文本，供 LLM 与规则解析使用。
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    texts: list[str] = []
    for page in doc:
        texts.append(page.get_text("text"))
    doc.close()
    return "\n".join(texts).strip()


def render_pdf_first_page_to_png(pdf_bytes: bytes, output_path: str) -> None:
    # 仅渲染首页作为预览图，平衡展示效果与性能。
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    try:
        page = doc[0]
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        pix.save(path)
    finally:
        doc.close()
