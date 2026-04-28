# 企业自动化发票报销系统 - 部署指南

本文档提供在全新 Ubuntu 24 Server 上部署该系统的详细步骤。

## 前置要求

### 硬件要求
- CPU: 2 核心及以上
- 内存: 2GB 及以上
- 磁盘: 20GB 及以上

### 软件要求
- Ubuntu 24 Server
- Docker 20.10+
- Docker Compose 2.0+

## 快速部署（推荐）

### 1. 安装 Docker 和 Docker Compose

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装 Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 安装 Docker Compose
sudo apt install docker-compose-plugin -y

# 验证安装
docker --version
docker compose version
```

### 2. 克隆项目

```bash
# 克隆项目到服务器
git clone <repository-url> /opt/invoice-system
cd /opt/invoice-system
```

### 3. 配置环境变量

```bash
# 复制环境变量模板
cp .env.docker .env

# 编辑环境变量（必须配置 LLM_API_KEY）
vim .env
```

**必须配置的环境变量：**

```env
LLM_API_KEY=your-actual-api-key-here  # 必须填写，否则无法解析发票
```

**可选配置：**

```env
LLM_API_BASE=https://api.deepseek.com  # LLM API 地址
LLM_MODEL=deepseek-chat               # LLM 模型名称
```

### 4. 启动服务

```bash
# 构建并启动所有服务（后台运行）
docker compose up -d

# 查看服务状态
docker compose ps

# 查看服务日志
docker compose logs -f
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

## 手动部署（开发/测试）

### 后端部署

```bash
# 安装 Python 3.11
sudo apt install python3.11 python3.11-venv python3-pip -y

# 创建虚拟环境
cd /opt/invoice-system/backend
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

### 前端部署

```bash
# 安装 Node.js 20
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# 安装依赖
cd /opt/invoice-system/frontend
npm install

# 配置环境变量（如需要）
cp .env.example .env
vim .env

# 开发模式启动
npm run dev -- --host 0.0.0.0 --port 5173

# 或构建生产版本
npm run build
npx serve -s dist -l 80
```

## 数据持久化

### Docker 部署数据持久化

以下目录已通过 volume 挂载，数据会持久化到宿主机：

| 宿主机路径 | 容器路径 | 说明 |
|------------|-----------|------|
| ./backend/source_files | /app/source_files | 源发票文件 |
| ./backend/archives | /app/archives | 归档发票文件 |
| ./backend/previews | /app/previews | 预览图 |
| ./backend/meta | /app/meta | 元数据文件 |
| ./backend/invoice.db | /app/invoice.db | SQLite 数据库 |

### 备份数据

```bash
# 备份数据库
cp backend/invoice.db backup/invoice.db.$(date +%Y%m%d)

# 备份文件
tar -czf backup/files.$(date +%Y%m%d).tar.gz backend/source_files backend/archives backend/previews backend/meta
```

## 常见问题

### Q1: 前端无法连接后端？

**检查项：**
1. 确认后端服务正在运行：`docker compose ps`
2. 检查后端日志：`docker compose logs backend`
3. 确认 LLM_API_KEY 已正确配置

### Q2: 上传发票显示解析失败？

**检查项：**
1. 确认 LLM_API_KEY 已配置且有效
2. 检查网络连接是否能访问 LLM API
3. 查看后端日志获取详细错误信息

### Q3: 局域网其他设备无法访问？

**解决方案：**
1. 确认服务绑定到 0.0.0.0（Docker 默认已配置）
2. 检查防火墙规则：`sudo ufw status`
3. 确认服务器 IP 地址正确

### Q4: 如何重启服务？

```bash
# 重启所有服务
docker compose restart

# 重启单个服务
docker compose restart backend
docker compose restart frontend
```

### Q5: 如何查看日志？

```bash
# 查看所有服务日志
docker compose logs -f

# 查看单个服务日志
docker compose logs -f backend
docker compose logs -f frontend

# 查看最近 100 行日志
docker compose logs --tail=100
```

### Q6: 如何更新项目？

```bash
# 拉取最新代码
git pull

# 重新构建并启动
docker compose up -d --build
```

## 生产环境优化建议

### 1. 使用 Nginx 反向代理（可选）

如果需要域名访问，可以配置 Nginx 反向代理：

```nginx
server {
    listen 80;
    server_name invoice.yourdomain.com;

    location / {
        proxy_pass http://localhost:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 2. 配置 HTTPS（推荐）

使用 Let's Encrypt 免费证书：

```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx -y

# 获取证书
sudo certbot --nginx -d invoice.yourdomain.com

# 自动续期
sudo certbot renew --dry-run
```

### 3. 配置自动备份

创建定时任务：

```bash
# 编辑 crontab
crontab -e

# 每天凌晨 2 点备份数据
0 2 * * * cd /opt/invoice-system && ./backup.sh
```

备份脚本示例（backup.sh）：

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

## 监控和维护

### 健康检查

```bash
# 检查服务状态
docker compose ps

# 检查后端健康
curl http://localhost:8000/health

# 检查前端访问
curl -I http://localhost:80
```

### 资源监控

```bash
# 查看 Docker 容器资源使用
docker stats

# 查看磁盘使用
df -h

# 查看内存使用
free -h
```

## 联系支持

如有问题，请查看：
- [README.md](./README.md) - 项目文档
- [项目规则](./.trae/project_rules.md) - 开发规范
- GitHub Issues - 提交问题
