#!/usr/bin/env bash
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info()  { echo -e "${GREEN}[INFO]${NC} $*"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*"; }

if [[ $EUID -ne 0 ]]; then
  log_error "请使用 sudo 或 root 用户运行此脚本"
  exit 1
fi

log_info "停止服务..."
systemctl stop invoice-backend invoice-frontend 2>/dev/null || true

log_info "禁用开机自启..."
systemctl disable invoice-backend invoice-frontend 2>/dev/null || true

log_info "移除 systemd 服务文件..."
rm -f /etc/systemd/system/invoice-backend.service
rm -f /etc/systemd/system/invoice-frontend.service
systemctl daemon-reload

if [[ -d /etc/systemd/system/invoice-backend.service.d ]]; then
  rm -rf /etc/systemd/system/invoice-backend.service.d
fi

log_info "服务已完全卸载"

echo ""
log_info "项目文件保留在磁盘上，未删除。"
log_warn "如需彻底清除项目文件，请手动删除项目目录。"
