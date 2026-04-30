#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
BACKEND_DIR="${PROJECT_ROOT}/backend"

cd "${BACKEND_DIR}"

if [[ ! -f ".env" ]]; then
  echo "[ERROR] 缺少 backend/.env，请复制 .env.example 并填写 LLM_API_KEY"
  exit 1
fi

if [[ ! -x ".venv/bin/uvicorn" ]]; then
  echo "[ERROR] 缺少 .venv/bin/uvicorn，请先运行 deploy/install.sh 安装依赖"
  exit 1
fi

exec .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
