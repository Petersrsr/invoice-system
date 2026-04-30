# 企业自动化发票报销系统 - 部署指南

## 前置要求

| 依赖 | 版本 |
|------|------|
| 操作系统 | Ubuntu 24 Server（其他 Linux 发行版类似） |
| Python | 3.11+ |
| Node.js | 20+ |
| 权限 | root 或 sudo |

### 硬件要求

- CPU: 2 核心及以上
- 内存: 2GB 及以上
- 磁盘: 20GB 及以上

## 一键部署

### 1. 克隆项目

```bash
git clone <repository-url> /opt/invoice-system
cd /opt/invoice-system
```

### 2. 运行安装脚本

```bash
sudo bash deploy/install.sh
```

脚本会自动完成以下操作：

1. 检测并安装缺失的系统依赖（Python、Node.js）
2. 创建 `www` 系统用户
3. 配置后端虚拟环境和依赖
4. 构建前端生产版本
5. 生成 systemd 服务文件并启动

#### 自定义参数

```bash
# 自定义端口和服务用户
sudo BACKEND_PORT=8000 FRONTEND_PORT=80 SERVICE_USER=www bash deploy/install.sh
```

### 3. 配置后端环境变量（必填）

```bash
sudo vim /opt/invoice-system/backend/.env
```

填入你的 LLM API Key：

```
LLM_API_KEY=your-api-key-here
```

修改配置后重启后端：

```bash
sudo systemctl restart invoice-backend
```

### 4. 验证部署

| 服务 | 地址 | 说明 |
|------|------|------|
| 前端界面 | http://服务器IP:80 | 员工和会计访问入口 |
| 后端 API | http://服务器IP:8000 | API 接口 |
| API 文档 | http://服务器IP:8000/docs | Swagger 文档 |
| 健康检查 | http://服务器IP:8000/health | 返回 `{"status":"ok"}` |

## 服务管理

### systemd 命令

```bash
# 查看状态
sudo systemctl status invoice-backend invoice-frontend

# 启动 / 停止 / 重启
sudo systemctl start   invoice-backend invoice-frontend
sudo systemctl stop    invoice-backend invoice-frontend
sudo systemctl restart invoice-backend invoice-frontend

# 查看日志
journalctl -u invoice-backend  -f
journalctl -u invoice-frontend -f
```

### 卸载服务

```bash
sudo bash deploy/uninstall.sh
```

仅停止并移除 systemd 服务，项目文件保留在磁盘上。

## 项目结构

```
deploy/
├── install.sh                              # 一键安装脚本
├── uninstall.sh                            # 一键卸载脚本
├── start_backend.sh                        # 后端启动入口
├── start_frontend.sh                       # 前端启动入口
└── systemd/
    ├── invoice-backend.service.in          # 后端服务模板
    └── invoice-frontend.service.in         # 前端服务模板
```

## 防火墙配置

```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8000/tcp
sudo ufw enable
```

## 数据持久化

以下路径在服务器迁移或重装时需要备份：

| 路径 | 说明 | 重要性 |
|------|------|--------|
| `backend/invoice.db` | SQLite 数据库 | **极高** |
| `backend/source_files/` | 原始 PDF 文件 | 高 |
| `backend/archives/` | 归档发票文件 | 高 |
| `backend/previews/` | 预览图 | 中 |
| `backend/meta/` | 元信息 JSON | 中 |
| `backend/.env` | 环境变量配置 | 高 |

## 常见问题

### 上传发票显示解析失败？

1. 检查 `backend/.env` 中的 `LLM_API_KEY` 是否正确
2. 确认 API Key 有足够的调用配额
3. 查看后端日志：`journalctl -u invoice-backend -n 50`

### 局域网其他设备无法访问？

1. 确认后端绑定 `0.0.0.0`（启动脚本已默认配置）
2. 检查防火墙是否放行 80 和 8000 端口
3. 确认 systemd 服务正常运行：`systemctl status invoice-backend`

### 如何修改监听端口？

重新运行安装脚本时传入环境变量：

```bash
sudo FRONTEND_PORT=8080 BACKEND_PORT=9000 bash deploy/install.sh
```

### 草稿和正式提交的区别？

| 特性 | 草稿模式 | 正式提交 |
|------|----------|----------|
| 去重检测 | 不检测 | 检测 |
| 状态 | draft | pending |
| 用途 | 先查看解析结果再决定 | 直接提交审批 |
