from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import sqlite3

from app.api.routes.invoices import router as invoice_router
from app.core.config import settings
from app.db.database import Base, engine


# 启动时创建缺失表（MVP 阶段不引入迁移工具）。
Base.metadata.create_all(bind=engine)
_SQLITE_EXTRA_COLUMNS: dict[str, str] = {
    "source_file_name": "VARCHAR(255)",
    "archived_file_name": "VARCHAR(255)",
    "invoice_number": "VARCHAR(128)",
    "uploader_name": "VARCHAR(128)",
    "approval_status": "VARCHAR(32)",
    "approval_comment": "TEXT",
    "approver_name": "VARCHAR(128)",
    "approved_at": "TIMESTAMP",
}


def _ensure_sqlite_columns() -> None:
    # 兼容历史 SQLite：在旧库缺少新增字段时自动补齐。
    if not settings.database_url.startswith("sqlite:///"):
        return
    db_path = settings.database_url.replace("sqlite:///", "", 1)
    conn = sqlite3.connect(db_path)
    try:
        rows = conn.execute("PRAGMA table_info(invoice_records)").fetchall()
        existing = {row[1] for row in rows}
        for col, col_type in _SQLITE_EXTRA_COLUMNS.items():
            if col not in existing:
                conn.execute(f"ALTER TABLE invoice_records ADD COLUMN {col} {col_type}")
        conn.commit()
    finally:
        conn.close()


_ensure_sqlite_columns()

app = FastAPI(title=settings.app_name)

# 当前为内网 MVP，CORS 先全开，后续应收敛白名单。
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(invoice_router, prefix="/api/invoices", tags=["invoices"])

# 保证审计相关目录在服务启动前存在，避免静态文件挂载失败。
for path in (settings.source_dir, settings.archive_dir, settings.preview_dir, settings.meta_dir):
    Path(path).mkdir(parents=True, exist_ok=True)

app.mount("/files/source", StaticFiles(directory=settings.source_dir), name="source-files")
app.mount("/files/archive", StaticFiles(directory=settings.archive_dir), name="archive-files")
app.mount("/files/preview", StaticFiles(directory=settings.preview_dir), name="preview-files")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
