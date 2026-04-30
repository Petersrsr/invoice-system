#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_PORT="${FRONTEND_PORT:-80}"
SERVICE_USER="${SERVICE_USER:-www}"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info()  { echo -e "${GREEN}[INFO]${NC} $*"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*"; }

check_root() {
  if [[ $EUID -ne 0 ]]; then
    log_error "请使用 sudo 或 root 用户运行此脚本"
    exit 1
  fi
}

detect_python() {
  local candidates=("python3.11" "python3.12" "python3.13" "python3")
  for cmd in "${candidates[@]}"; do
    if command -v "$cmd" &>/dev/null; then
      PYTHON_CMD="$cmd"
      return 0
    fi
  done
  log_error "未找到 Python 3.11+，请先安装"
  exit 1
}

detect_node() {
  if command -v node &>/dev/null; then
    local ver
    ver=$(node -v | sed 's/v//' | cut -d. -f1)
    if [[ "$ver" -ge 20 ]]; then
      NODE_AVAILABLE=1
      return 0
    fi
  fi
  NODE_AVAILABLE=0
}

ensure_system_deps() {
  log_info "检查系统依赖..."

  apt-get update -qq

  if ! command -v python3 &>/dev/null; then
    log_info "安装 Python..."
    apt-get install -y python3 python3-venv python3-pip
  fi
  detect_python
  log_info "Python: $($PYTHON_CMD --version)"

  detect_node
  if [[ "$NODE_AVAILABLE" -eq 0 ]]; then
    log_warn "未找到 Node.js 20+，正在安装..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt-get install -y nodejs
    log_info "Node.js: $(node --version)"
  else
    log_info "Node.js: $(node --version)"
  fi
}

ensure_service_user() {
  if id "$SERVICE_USER" &>/dev/null; then
    log_info "用户 '$SERVICE_USER' 已存在"
  else
    log_info "创建系统用户 '$SERVICE_USER'..."
    useradd -r -s /bin/false -d "$PROJECT_ROOT" "$SERVICE_USER"
    log_info "用户 '$SERVICE_USER' 已创建"
  fi
}

setup_backend() {
  log_info "配置后端..."
  local backend_dir="${PROJECT_ROOT}/backend"
  cd "$backend_dir"

  if [[ ! -d ".venv" ]]; then
    log_info "创建 Python 虚拟环境..."
    "$PYTHON_CMD" -m venv .venv
  fi

  log_info "安装后端依赖..."
  .venv/bin/pip install -q -r requirements.txt

  if [[ ! -f ".env" ]]; then
    cp .env.example .env
    log_warn "已创建 backend/.env，请编辑填入 LLM_API_KEY"
  fi

  mkdir -p source_files archives previews meta

  chown -R "$SERVICE_USER:$SERVICE_USER" "$backend_dir"
  log_info "后端配置完成"
}

setup_frontend() {
  log_info "配置前端..."
  local frontend_dir="${PROJECT_ROOT}/frontend"
  cd "$frontend_dir"

  log_info "安装前端依赖..."
  npm install --no-fund --no-audit -q

  log_info "构建前端生产版本..."
  npm run build

  if [[ ! -f ".env" ]]; then
    cp .env.example .env
  fi

  chown -R "$SERVICE_USER:$SERVICE_USER" "$frontend_dir"
  log_info "前端配置完成"
}

setup_systemd() {
  log_info "配置 systemd 服务..."

  chown -R "$SERVICE_USER:$SERVICE_USER" "$PROJECT_ROOT"

  local backend_env_file="${PROJECT_ROOT}/backend/.env"

  sed \
    -e "s|__PROJECT_ROOT__|${PROJECT_ROOT}|g" \
    -e "s|__SERVICE_USER__|${SERVICE_USER}|g" \
    -e "s|__BACKEND_PORT__|${BACKEND_PORT}|g" \
    "${SCRIPT_DIR}/systemd/invoice-backend.service.in" \
    > /etc/systemd/system/invoice-backend.service

  sed \
    -e "s|__PROJECT_ROOT__|${PROJECT_ROOT}|g" \
    -e "s|__SERVICE_USER__|${SERVICE_USER}|g" \
    -e "s|__FRONTEND_PORT__|${FRONTEND_PORT}|g" \
    "${SCRIPT_DIR}/systemd/invoice-frontend.service.in" \
    > /etc/systemd/system/invoice-frontend.service

  systemctl daemon-reload
  systemctl enable invoice-backend invoice-frontend

  log_info "systemd 服务已配置并启用开机自启"
}

start_services() {
  log_info "启动服务..."
  systemctl start invoice-backend
  systemctl start invoice-frontend

  sleep 2

  if systemctl is-active --quiet invoice-backend; then
    log_info "后端服务已启动 (端口 ${BACKEND_PORT})"
  else
    log_error "后端服务启动失败，查看: journalctl -u invoice-backend -n 20"
  fi

  if systemctl is-active --quiet invoice-frontend; then
    log_info "前端服务已启动 (端口 ${FRONTEND_PORT})"
  else
    log_error "前端服务启动失败，查看: journalctl -u invoice-frontend -n 20"
  fi
}

print_summary() {
  local ip
  ip=$(hostname -I 2>/dev/null | awk '{print $1}' || echo "服务器IP")

  echo ""
  echo "=========================================="
  log_info "部署完成!"
  echo "=========================================="
  echo ""
  echo "  前端地址:  http://${ip}:${FRONTEND_PORT}"
  echo "  后端 API:  http://${ip}:${BACKEND_PORT}"
  echo "  API 文档:  http://${ip}:${BACKEND_PORT}/docs"
  echo "  健康检查:  http://${ip}:${BACKEND_PORT}/health"
  echo ""
  echo "  服务管理:"
  echo "    sudo systemctl status  invoice-backend invoice-frontend"
  echo "    sudo systemctl restart invoice-backend invoice-frontend"
  echo "    sudo systemctl stop    invoice-backend invoice-frontend"
  echo "    journalctl -u invoice-backend  -f"
  echo "    journalctl -u invoice-frontend -f"
  echo ""
}

main() {
  check_root
  ensure_system_deps
  ensure_service_user
  setup_backend
  setup_frontend
  setup_systemd
  start_services
  print_summary
}

main "$@"
