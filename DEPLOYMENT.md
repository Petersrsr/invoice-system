# 企业自动化发票报销系统 - 部署指南

本文档提供在全新 Ubuntu 24 Server 上部署该系统的详细步骤。

## 前置要求

### 硬件要求
- CPU: 2 核心及以上
- 内存: 2GB 及以上
- 磁盘: 20GB 及以上

### 软件要求
- Ubuntu 24 Server
- Python 3.11+
- Node.js 20+
- npm

## 快速部署

### 1. 安装系统依赖

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装 Python 3.11
sudo apt install python3.11 python3.11-venv python3-pip -y

# 安装 Node.js 20
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# 验证安装
python3.11 --version
node --version
npm --version
```

### 2. 克隆项目

```bash
# 克隆项目到服务器
git clone <repository-url> /opt/invoice-system
cd /opt/invoice-system
```

### 3. 后端部署

```bash
# 进入后端目录
cd /opt/invoice-system/backend

# 创建虚拟环境
python3.11 -m venv .venv
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
vim .env  # 填写 LLM_API_KEY

# 创建必要目录
mkdir -p source_files archives previews meta

# 启动服务（开发模式，支持热重载）
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. 前端部署

```bash
# 进入前端目录
cd /opt/invoice-system/frontend

# 安装依赖
npm install

# 配置环境变量（如需要）
cp .env.example .env
vim .env

# 构建生产版本
npm run build

# 使用 serve 提供静态文件服务
npx serve -s dist -l 80
```

### 5. 验证部署

| 服务 | 地址 | 说明 |
|------|------|------|
| 前端 | http://服务器IP:80 | 员工和会计访问入口 |
| 后端 API | http://服务器IP:8000 | API 接口 |
| Swagger 文档 | http://服务器IP:8000/docs | API 文档 |

### 6. 配置防火墙（如需要）

```bash
# 允许 HTTP 和 HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 如果需要直接访问后端 API
sudo ufw allow 8000/tcp

# 启用防火墙
sudo ufw enable
```

## 生产环境部署

### 使用 systemd 管理服务

#### 1. 后端 systemd 服务

创建服务文件：

```bash
sudo vim /etc/systemd/system/invoice-backend.service
```

内容：

```ini
[Unit]
Description=Invoice System Backend (FastAPI)
After=network.target

[Service]
Type=simple
User=www
Group=www
WorkingDirectory=/opt/invoice-system/backend
ExecStart=/opt/invoice-system/backend/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=3
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```

#### 2. 前端 systemd 服务

创建服务文件：

```bash
sudo vim /etc/systemd/system/invoice-frontend.service
```

内容：

```ini
[Unit]
Description=Invoice System Frontend (Vite Preview)
After=network.target

[Service]
Type=simple
User=www
Group=www
WorkingDirectory=/opt/invoice-system/frontend
ExecStart=/opt/invoice-system/frontend/node_modules/.bin/serve -s dist -l 80
Restart=always
RestartSec=3
Environment=NODE_ENV=production

[Install]
WantedBy=multi-user.target
```

#### 3. 启动服务

```bash
# 重新加载 systemd 配置
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start invoice-backend
sudo systemctl start invoice-frontend

# 设置开机自启
sudo systemctl enable invoice-backend
sudo systemctl enable invoice-frontend

# 查看服务状态
sudo systemctl status invoice-backend
sudo systemctl status invoice-frontend
```

## 数据持久化

以下目录/文件需要在部署时持久化存储：

| 路径 | 说明 | 重要性 |
|------|------|--------|
| backend/source_files | 源发票文件 | 高 |
| backend/archives | 归档发票文件 | 高 |
| backend/previews | 预览图 | 中 |
| backend/meta | 元信息文件 | 中 |
| backend/invoice.db | SQLite 数据库 | **极高** |

## 备份策略

### 1. 创建备份脚本

```bash
vim /opt/invoice-system/backup.sh
```

内容：

```bash
#!/bin/bash
BACKUP_DIR="/opt/invoice-system/backup"
DATE=$(date +%Y%m%d)

mkdir -p $BACKUP_DIR

# 备份数据库
cp backend/invoice.db $BACKUP_DIR/invoice.db.$DATE

# 备份文件
tar -czf $BACKUP_DIR/files.$DATE.tar.gz backend/source_files backend/archives backend/previews backend/meta

# 删除 7 天前的备份
find $BACKUP_DIR -name "*.db.*" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

### 2. 设置定时任务

```bash
# 编辑 crontab
crontab -e

# 每天凌晨 2 点备份数据
0 2 * * * /opt/invoice-system/backup.sh
```

## 常见问题

### Q1: 上传发票显示解析失败？

**可能原因：**
1. LLM API Key 未配置或已过期
2. PDF 文件损坏或非标准格式
3. 网络连接问题

**解决方案：**
- 检查 backend/.env 中的 LLM_API_KEY 是否正确
- 确认 API Key 有足够的调用配额
- 检查后端服务日志获取详细错误信息

### Q2: 局域网其他设备无法访问？

**解决方案：**
1. 确保后端绑定到 `0.0.0.0` 而非 `127.0.0.1`
2. 检查防火墙是否放行对应端口
3. 前端开发模式启动时添加 `--host` 参数

### Q3: 如何开启调试模式？

**后端调试：**
```bash
cd /opt/invoice-system/backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**前端热更新：**
```bash
cd /opt/invoice-system/frontend
npm run dev -- --host 0.0.0.0 --port 5173
```

### Q4: 草稿和正式提交有什么区别？

| 特性 | 草稿模式 | 正式提交 |
|------|----------|----------|
| 去重检测 | 不检测 | 检测 |
| 状态 | draft | pending |
| 用途 | 修改信息后重新上传 | 提交审批 |

## 监控和维护

### 健康检查

```bash
# 检查服务状态
sudo systemctl status invoice-backend
sudo systemctl status invoice-frontend

# 检查后端健康
curl http://localhost:8000/health

# 检查前端访问
curl -I http://localhost:80
```

### 资源监控

```bash
# 查看进程资源使用
top -p $(pgrep -f "uvicorn|serve")

# 查看磁盘使用
df -h

# 查看内存使用
free -h
```

## 联系支持

如有问题，请查看：
- [README.md](./README.md) - 项目文档
- GitHub Issues - 提交问题
