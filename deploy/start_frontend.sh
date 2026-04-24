#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
FRONTEND_DIR="${PROJECT_ROOT}/frontend"

cd "${FRONTEND_DIR}"

if [[ ! -d "node_modules" ]]; then
  echo "缺少 frontend/node_modules，请先执行 npm install。"
  exit 1
fi

npm run build
exec npm run preview -- --host 0.0.0.0 --port 4173
