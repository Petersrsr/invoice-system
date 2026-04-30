#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
FRONTEND_DIR="${PROJECT_ROOT}/frontend"

cd "${FRONTEND_DIR}"

if [[ ! -d "node_modules" ]]; then
  echo "[ERROR] 缺少 node_modules，请先运行 deploy/install.sh 安装依赖"
  exit 1
fi

if [[ ! -d "dist" ]]; then
  echo "[INFO] 首次启动，正在构建前端..."
  npm run build
fi

exec npm run preview -- --host 0.0.0.0 --port 80
