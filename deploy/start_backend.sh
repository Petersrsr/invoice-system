#!/usr/bin/env bash
set -euo pipefail

# 基于脚本位置推导项目根目录，避免依赖调用时 cwd。
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
BACKEND_DIR="${PROJECT_ROOT}/backend"

cd "${BACKEND_DIR}"

if [[ ! -x ".venv/bin/uvicorn" ]]; then
  echo "缺少 backend/.venv/bin/uvicorn，请先在 backend 目录安装依赖。"
  exit 1
fi

# 生产以非 reload 模式启动，交由 systemd 守护。
exec .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
