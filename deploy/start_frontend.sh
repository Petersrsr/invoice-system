#!/usr/bin/env bash
set -euo pipefail

# 基于脚本位置推导项目根目录，避免依赖调用时 cwd。
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
FRONTEND_DIR="${PROJECT_ROOT}/frontend"

cd "${FRONTEND_DIR}"

if [[ ! -d "node_modules" ]]; then
  echo "缺少 frontend/node_modules，请先执行 npm install。"
  exit 1
fi

# 先构建再 preview，确保 systemd 始终对外提供构建产物。
npm run build
# 对外监听 80 端口（配合 systemd 能力授权）。
exec npm run preview -- --host 0.0.0.0 --port 80
