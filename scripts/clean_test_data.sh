#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
BACKEND_DIR="${PROJECT_ROOT}/backend"
DB_PATH="${BACKEND_DIR}/invoice.db"

TARGET_DIRS=(
  "${BACKEND_DIR}/previews"
  "${BACKEND_DIR}/source_files"
  "${BACKEND_DIR}/archives"
  "${BACKEND_DIR}/meta"
)

echo "[clean] project root: ${PROJECT_ROOT}"

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

python3 - <<PY
import sqlite3
from pathlib import Path

db = Path(r"${DB_PATH}")
conn = sqlite3.connect(db)
try:
    table = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='invoice_records'"
    ).fetchone()
    if not table:
        print("[clean] table invoice_records not found, skip database cleanup")
    else:
        conn.execute("DELETE FROM invoice_records")
        has_seq = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='sqlite_sequence'"
        ).fetchone()
        if has_seq:
            conn.execute("DELETE FROM sqlite_sequence WHERE name='invoice_records'")
        conn.commit()
        remaining = conn.execute("SELECT COUNT(*) FROM invoice_records").fetchone()[0]
        print(f"[clean] invoice_records rows after cleanup: {remaining}")
finally:
    conn.close()
PY

echo "[clean] done"
