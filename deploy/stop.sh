#!/usr/bin/env bash
set -euo pipefail

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

stop_service() {
  local name="$1"
  if systemctl is-active --quiet "$name" 2>/dev/null; then
    systemctl stop "$name"
    log_info "${name} 已停止"
  else
    log_warn "${name} 未在运行"
  fi

  if systemctl is-enabled --quiet "$name" 2>/dev/null; then
    systemctl disable "$name" 2>/dev/null
    log_info "${name} 已取消开机自启"
  fi
}

main() {
  check_root

  echo ""
  log_info "停止发票报销系统服务..."
  echo ""

  stop_service invoice-backend
  stop_service invoice-frontend

  echo ""
  log_info "所有服务已停止"
  echo ""
  echo "  如需重新启动："
  echo "    sudo systemctl start invoice-backend invoice-frontend"
  echo ""
  echo "  如需完全卸载："
  echo "    sudo bash $(dirname "$0")/uninstall.sh"
  echo ""
}

main "$@"
