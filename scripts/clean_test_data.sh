#!/usr/bin/env bash
set -euo pipefail

# 清理脚本：删除测试文件并清空 invoice_records，便于重复联调。
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
BACKEND_DIR="${PROJECT_ROOT}/backend"
BACKEND_ENV_FILE="${BACKEND_DIR}/.env"
DEFAULT_DB_PATH="${BACKEND_DIR}/invoice.db"
DB_PATH="${DEFAULT_DB_PATH}"

if [[ -f "${BACKEND_ENV_FILE}" ]]; then
  # 从 .env 读取 DATABASE_URL，支持 sqlite:///./invoice.db 这类相对路径写法。
  db_url_line="$(grep -E '^[[:space:]]*DATABASE_URL=' "${BACKEND_ENV_FILE}" | tail -n 1 || true)"
  if [[ -n "${db_url_line}" ]]; then
    db_url="${db_url_line#*=}"
    db_url="${db_url//\"/}"
    db_url="${db_url//\'/}"
    if [[ "${db_url}" == sqlite:///* ]]; then
      db_raw_path="${db_url#sqlite:///}"
      if [[ "${db_raw_path}" = /* ]]; then
        DB_PATH="${db_raw_path}"
      else
        DB_PATH="${BACKEND_DIR}/${db_raw_path#./}"
      fi
    fi
  fi
fi

TARGET_DIRS=(
  "${BACKEND_DIR}/previews"
  "${BACKEND_DIR}/source_files"
  "${BACKEND_DIR}/archives"
  "${BACKEND_DIR}/meta"
)

echo "[clean] project root: ${PROJECT_ROOT}"
echo "[clean] sqlite db path: ${DB_PATH}"

if command -v systemctl >/dev/null 2>&1; then
  backend_active="$(systemctl is-active invoice-backend 2>/dev/null || true)"
  if [[ "${backend_active}" == "active" ]]; then
    cat <<'EOF'
[warn] 检测到 invoice-backend 正在运行，SQLite 可能被占用导致清理失败。
[warn] 建议先执行：sudo systemctl stop invoice-backend
[warn] 清理完成后再执行：sudo systemctl start invoice-backend
EOF
    read -r -p "继续清理吗？[y/N] " confirm
    if [[ ! "${confirm}" =~ ^[Yy]$ ]]; then
      echo "[clean] 已取消。"
      exit 0
    fi
  fi
fi

for dir in "${TARGET_DIRS[@]}"; do
  mkdir -p "${dir}"
  count_before="$(find "${dir}" -mindepth 1 -maxdepth 1 | wc -l || true)"
  if [[ "${count_before}" -gt 0 ]]; then
    find "${dir}" -mindepth 1 -maxdepth 1 -exec rm -rf {} +
  fi
  echo "[clean] ${dir}: ${count_before} -> 0"
done

if [[ ! -f "${DB_PATH}" ]]; then
  echo "[clean] database not found, skip: ${DB_PATH}"
  exit 0
fi

# 使用内联 Python 执行 SQLite 清表与自增序列重置。
python3 - <<PY
import time
import sqlite3
from pathlib import Path

db = Path(r"${DB_PATH}")
max_retries = 3
for attempt in range(1, max_retries + 1):
    conn = sqlite3.connect(db, timeout=8)
    try:
        table = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='invoice_records'"
        ).fetchone()
        if not table:
            print("[clean] table invoice_records not found, skip database cleanup")
            break
        conn.execute("DELETE FROM invoice_records")
        has_seq = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='sqlite_sequence'"
        ).fetchone()
        if has_seq:
            conn.execute("DELETE FROM sqlite_sequence WHERE name='invoice_records'")
        conn.commit()
        remaining = conn.execute("SELECT COUNT(*) FROM invoice_records").fetchone()[0]
        print(f"[clean] invoice_records rows after cleanup: {remaining}")
        break
    except sqlite3.OperationalError as exc:
        msg = str(exc).lower()
        if "locked" in msg and attempt < max_retries:
            print(f"[clean] sqlite locked, retry {attempt}/{max_retries} ...")
            time.sleep(1.2)
            continue
        raise
    finally:
        conn.close()
PY

echo "[clean] done"
