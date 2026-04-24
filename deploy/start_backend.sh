#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
BACKEND_DIR="${PROJECT_ROOT}/backend"

cd "${BACKEND_DIR}"

if [[ ! -x ".venv/bin/uvicorn" ]]; then
  echo "缺少 backend/.venv/bin/uvicorn，请先在 backend 目录安装依赖。"
  exit 1
fi

exec .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
