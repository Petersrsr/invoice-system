# 企业自动化发票报销系统

一个面向企业内部的自动化发票报销系统，支持发票上传、智能解析、草稿编辑、归档管理、审批流程和统计报表。

## 功能特性

### 核心功能

| 功能 | 说明 |
|------|------|
| **发票上传** | 支持拖拽上传 PDF 发票文件（最大 10MB） |
| **智能解析** | 使用 LLM（大语言模型）自动提取发票字段：金额、日期、销售方、税号、品名、发票号码等 |
| **草稿机制** | 上传后默认为草稿状态，支持修改信息后重新上传，不触发去重检测 |
| **确认提交** | 草稿确认后进入待审批状态，此时进行去重检测 |
| **自动归档** | 按规则命名并存储源文件和归档文件 |
| **去重策略** | 正式提交时检测重复发票号，自动覆盖旧文件并更新记录 |
| **预览查看** | 支持源文件下载、归档文件下载、预览图查看 |
| **放大预览** | 点击预览图可放大至全屏查看 |
| **审批流程** | 三种审批状态：待审批（pending）、已批准（approved）、已拒绝（rejected） |
| **彻底删除** | 删除发票时同时删除数据库记录和所有相关文件（源文件、归档文件、预览图、元数据） |
| **统计报表** | 发票数量统计、金额汇总、审批状态分布、用途分布、报销金额排行 |

### 页面说明

| 页面 | 路径 | 说明 |
|------|------|------|
| 员工上传页 | `/` | 发票上传入口，填写上传人姓名后上传 PDF 文件 |
| 会计审批页 | `/accountant` | 发票列表展示、统计报表、审批操作 |

## 技术栈

### 后端

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.11+ | 编程语言 |
| FastAPI | 0.115+ | Web 框架 |
| SQLAlchemy | 2.0+ | ORM |
| Pydantic | 2.0+ | 数据验证 |
| PyMuPDF | 1.24+ | PDF 解析 |
| httpx | 0.27+ | HTTP 客户端 |
| SQLite | - | 数据库 |

### 前端

| 技术 | 版本 | 用途 |
|------|------|------|
| Vue | 3.5+ | 渐进式框架 |
| TypeScript | 5.6+ | 类型安全 |
| Vite | 5.4+ | 构建工具 |
| Tailwind CSS | 3.4+ | 样式框架 |
| Axios | 1.8+ | HTTP 客户端 |
| Vue Router | 4.6+ | 路由管理 |

## 快速开始

### 环境要求

- Python 3.11+
- Node.js 20+
- npm 或 yarn
- Docker（可选，用于容器化部署）

### 开发模式

#### 1. 克隆项目

```bash
git clone <repository-url>
cd invoice-system
```

#### 2. 配置后端环境变量

```bash
cd backend
cp .env.example .env
# 编辑 .env 文件，配置 LLM_API_KEY（必填）
```

#### 3. 安装后端依赖并启动

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 4. 安装前端依赖并启动

```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```

#### 5. 访问地址

| 服务 | 地址 |
|------|------|
| 前端（开发） | http://localhost:5173 |
| 后端 API | http://localhost:8000 |
| Swagger 文档 | http://localhost:8000/docs |

### Docker 部署（推荐）

#### 1. 配置环境变量

```bash
cp .env.docker .env
# 编辑 .env 文件，配置 LLM_API_KEY（必填）
```

#### 2. 启动服务

```bash
docker-compose up -d
```

#### 3. 访问地址

| 服务 | 地址 |
|------|------|
| 前端 | http://服务器IP:80 |
| 后端 API | http://服务器IP:8000 |
| Swagger 文档 | http://服务器IP:8000/docs |

## 项目结构

```
invoice-system/
├── backend/                          # 后端服务
│   ├── app/                          # 应用代码
│   │   ├── main.py                   # 入口文件
│   │   ├── core/                     # 核心配置
│   │   │   └── config.py             # 配置管理（环境变量）
│   │   ├── db/                       # 数据库相关
│   │   │   ├── database.py           # 数据库连接
│   │   │   └── models.py             # 数据模型（SQLAlchemy）
│   │   ├── api/                      # API 路由
│   │   │   └── routes/
│   │   │       └── invoices.py       # 发票相关 API
│   │   ├── schemas/                  # Pydantic 模型
│   │   │   └── invoice.py            # 发票数据结构
│   │   └── services/                 # 业务服务
│   │       ├── pdf_parser.py         # PDF 解析服务
│   │       ├── llm_client.py         # LLM 客户端
│   │       └── invoice_service.py    # 发票业务逻辑
│   ├── archives/                     # 归档发票文件存储
│   ├── source_files/                 # 源发票文件存储
│   ├── previews/                     # 预览图存储
│   ├── meta/                         # 元信息存储
│   ├── invoice.db                    # SQLite 数据库文件
│   ├── Dockerfile                    # 后端 Docker 配置
│   ├── requirements.txt              # Python 依赖
│   └── .env                          # 环境变量配置
├── frontend/                          # 前端应用
│   ├── src/                          # 源代码
│   │   ├── main.ts                  # 入口文件
│   │   ├── App.vue                  # 根组件
│   │   ├── api/                     # API 调用
│   │   │   └── invoice.ts          # 发票 API 封装
│   │   ├── components/              # UI 组件
│   │   │   ├── InvoiceUpload.vue   # 上传组件
│   │   │   └── InvoiceTable.vue    # 表格组件（含删除功能）
│   │   ├── views/                  # 页面视图
│   │   │   ├── EmployeePage.vue    # 员工上传页
│   │   │   └── AccountantPage.vue  # 会计审批页
│   │   └── types/                  # TypeScript 类型
│   │       └── invoice.ts         # 发票类型定义
│   ├── dist/                        # 构建输出目录
│   ├── Dockerfile                   # 前端 Docker 配置
│   ├── nginx.conf                   # Nginx 反向代理配置
│   ├── package.json                 # npm 依赖
│   ├── vite.config.ts               # Vite 配置
│   └── .env                         # 环境变量配置
├── docker-compose.yml                # Docker Compose 配置
├── .env.docker                       # Docker 环境变量模板
└── README.md                         # 项目说明文档
```

## API 接口文档

### 基础信息

| 项目 | 值 |
|------|------|
| Base URL | `/api/invoices` |
| Content-Type | `multipart/form-data`（上传）或 `application/json`（其他） |
| 认证 | 无（内网 MVP） |

### 1. 上传发票

```
POST /api/invoices/upload
```

上传 PDF 发票文件，系统自动解析提取发票信息。

**请求体：** `multipart/form-data`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file | File | 是 | PDF 文件（最大 10MB） |
| uploader_name | string | 是 | 上传人姓名 |
| draft | boolean | 否 | 是否为草稿模式，默认 `true` |

**响应示例：**

```json
{
  "id": 1,
  "file_name": "矢吉-上海罗森-食品-100.00元-12345678.pdf",
  "uploader_name": "张三",
  "replaced": false,
  "message": "上传成功，已完成解析",
  "extracted": {
    "amount": 100.0,
    "date": "2026-04-01",
    "seller_name": "上海罗森便利有限公司",
    "purpose": "食品",
    "invoice_number": "12345678",
    "tax_id": "91310109XXXXXXXXX",
    "title": "上海罗森便利有限公司",
    "item_name": "食品"
  }
}
```

**特殊响应（检测到重复发票号）：**

```json
{
  "id": 2,
  "file_name": "矢吉-上海罗森-食品-100.00元-12345678.pdf",
  "uploader_name": "李四",
  "replaced": true,
  "message": "检测到重复发票号，已覆盖旧文件并更新记录",
  "extracted": {
    "amount": 100.0,
    "date": "2026-04-01",
    "seller_name": "上海罗森便利有限公司",
    "purpose": "食品",
    "invoice_number": "12345678",
    "tax_id": "91310109XXXXXXXXX",
    "title": "上海罗森便利有限公司",
    "item_name": "食品"
  }
}
```

### 2. 发票列表

```
GET /api/invoices
```

获取所有发票列表（按 id 倒序排列）。

**响应示例：**

```json
[
  {
    "id": 1,
    "file_name": "矢吉-上海罗森-食品-100.00元-12345678.pdf",
    "uploader_name": "张三",
    "amount": 100.0,
    "invoice_date": "2026-04-01",
    "seller_name": "上海罗森便利有限公司",
    "purpose": "食品",
    "invoice_number": "12345678",
    "tax_id": "91310109XXXXXXXXX",
    "title": "上海罗森便利有限公司",
    "item_name": "食品",
    "created_at": "2026-04-27T10:00:00",
    "approval_status": "pending"
  }
]
```

### 3. 发票详情

```
GET /api/invoices/{invoice_id}
```

获取单条发票详细信息，包含文件链接和预览图。

**路径参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| invoice_id | integer | 发票记录 ID |

**响应示例：**

```json
{
  "id": 1,
  "file_name": "矢吉-上海罗森-食品-100.00元-12345678.pdf",
  "uploader_name": "张三",
  "amount": 100.0,
  "invoice_date": "2026-04-01",
  "seller_name": "上海罗森便利有限公司",
  "purpose": "食品",
  "invoice_number": "12345678",
  "tax_id": "91310109XXXXXXXXX",
  "source_file_name": "source_abc123.pdf",
  "archived_file_name": "矢吉-上海罗森-食品-100.00元-12345678.pdf",
  "source_file_url": "/files/source/source_abc123.pdf",
  "archived_file_url": "/files/archive/矢吉-上海罗森-食品-100.00元-12345678.pdf",
  "source_preview_image_url": "/files/preview/1-source.png",
  "archive_preview_image_url": "/files/preview/1-archive.png",
  "preview_image_url": "/files/preview/1-archive.png",
  "raw_text": "原始发票文本内容...",
  "created_at": "2026-04-27T10:00:00",
  "approval_status": "pending",
  "approval_comment": null,
  "approver_name": null,
  "approved_at": null
}
```

### 4. 确认提交草稿

```
POST /api/invoices/{invoice_id}/confirm
```

将草稿状态的发票确认为正式记录，进入待审批状态，同时进行去重检测。

**路径参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| invoice_id | integer | 发票记录 ID |

**响应示例：**

```json
{
  "id": 1,
  "file_name": "矢吉-上海罗森-食品-100.00元-12345678.pdf",
  "uploader_name": "张三",
  "replaced": false,
  "message": "提交成功",
  "extracted": {
    "amount": 100.0,
    "date": "2026-04-01",
    "seller_name": "上海罗森便利有限公司",
    "purpose": "食品",
    "invoice_number": "12345678",
    "tax_id": "91310109XXXXXXXXX",
    "title": "上海罗森便利有限公司",
    "item_name": "食品"
  }
}
```

### 5. 取消并删除草稿

```
DELETE /api/invoices/{invoice_id}/cancel
```

取消并删除草稿状态的发票记录（仅适用于草稿）。

**路径参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| invoice_id | integer | 发票记录 ID |

**响应示例：**

```json
{
  "status": "ok",
  "message": "已取消并删除草稿"
}
```

### 6. 审批发票

```
POST /api/invoices/{invoice_id}/approve
```

审批发票（批准或拒绝）。

**路径参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| invoice_id | integer | 发票记录 ID |

**请求体：**

```json
{
  "status": "approved",
  "comment": "审批通过",
  "approver_name": "李四"
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| status | string | 是 | 审批状态：`approved`（批准）或 `rejected`（拒绝） |
| comment | string | 否 | 审批备注 |
| approver_name | string | 是 | 审批人姓名 |

**响应示例：**

```json
{
  "id": 1,
  "approval_status": "approved",
  "approval_comment": "审批通过",
  "approver_name": "李四",
  "approved_at": "2026-04-27T10:30:00"
}
```

### 7. 彻底删除发票

```
DELETE /api/invoices/{invoice_id}/delete
```

彻底删除发票记录及所有相关文件，包括：
- 数据库记录
- 源文件（source_files/）
- 归档文件（archives/）
- 预览图片（previews/）
- 元数据文件（meta/）

**路径参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| invoice_id | integer | 发票记录 ID |

**响应示例：**

```json
{
  "status": "ok",
  "message": "已彻底删除发票记录及所有相关文件"
}
```

### 8. 健康检查

```
GET /health
```

服务健康检查接口。

**响应示例：**

```json
{
  "status": "ok"
}
```

## 环境变量配置

### 后端环境变量（backend/.env）

| 变量名 | 默认值 | 必填 | 说明 |
|--------|--------|------|------|
| APP_ENV | production | 否 | 运行环境：`production` 或 `dev` |
| LLM_API_BASE | https://api.deepseek.com | 否 | LLM API 地址 |
| LLM_API_KEY | - | **是** | LLM API Key（需自行申请） |
| LLM_MODEL | deepseek-chat | 否 | LLM 模型名称 |
| DATABASE_URL | sqlite:///./invoice.db | 否 | 数据库连接地址 |

### 前端环境变量（frontend/.env）

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| VITE_API_BASE | `http://localhost:8000/api` | 后端 API 地址 |

## 数据库架构

### 发票记录表（invoice_records）

| 字段 | 类型 | 可空 | 默认值 | 说明 |
|------|------|------|--------|------|
| id | INTEGER | 否 | 自增 | 主键 |
| file_name | VARCHAR(255) | 否 | - | 归档文件名 |
| source_file_name | VARCHAR(255) | 是 | NULL | 源文件名 |
| archived_file_name | VARCHAR(255) | 是 | NULL | 归档文件名 |
| invoice_number | VARCHAR(128) | 是 | NULL | 发票号码 |
| uploader_name | VARCHAR(128) | 是 | NULL | 上传人姓名 |
| amount | FLOAT | 是 | NULL | 金额 |
| invoice_date | VARCHAR(50) | 是 | NULL | 发票日期 |
| title | VARCHAR(255) | 是 | NULL | 销售方名称 |
| tax_id | VARCHAR(64) | 是 | NULL | 税号 |
| item_name | VARCHAR(255) | 是 | NULL | 商品名称/用途 |
| raw_text | TEXT | 是 | NULL | 原始文本（审计用） |
| created_at | TIMESTAMP | 否 | 当前时间 | 创建时间 |
| approval_status | VARCHAR(32) | 否 | pending | 审批状态 |
| approval_comment | TEXT | 是 | NULL | 审批备注 |
| approver_name | VARCHAR(128) | 是 | NULL | 审批人 |
| approved_at | TIMESTAMP | 是 | NULL | 审批时间 |

### 数据库索引

| 索引名称 | 字段 | 用途 |
|----------|------|------|
| idx_invoice_number | invoice_number | 发票号去重查询 |
| idx_uploader_name | uploader_name | 上传人统计筛选 |
| idx_approval_status | approval_status | 审批状态筛选 |
| idx_created_at | created_at | 时间排序查询 |
| idx_status_date | approval_status, created_at | 组合条件查询 |

## 发票归档命名规则

归档文件命名格式：

```
{公司简称}-{销售方名称}-{用途}-{金额}元-{发票号码}.pdf
```

**命名示例：**

```
矢吉-上海罗森便利有限公司-食品-100.00元-26317000000980499812.pdf
```

**各字段说明：**

| 字段 | 示例 | 说明 |
|------|------|------|
| 公司简称 | 矢吉 | 固定前缀 |
| 销售方名称 | 上海罗森便利有限公司 | 从发票提取 |
| 用途 | 食品 | 从发票提取的商品类别 |
| 金额 | 100.00 | 从发票提取的交易金额 |
| 发票号码 | 26317000000980499812 | 从发票提取的唯一号码 |

## 业务流程

### 发票上传流程图

```
┌──────────────────────────────────────────────────────────────┐
│                     发票上传流程                              │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  员工上传 PDF    │
                    └────────┬────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ 系统解析 PDF    │
                    │ 提取发票信息    │
                    └────────┬────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ 保存为草稿状态  │
                    │ (draft=true)    │
                    │ 不触发去重检测  │
                    └────────┬────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ 员工确认信息    │
                    │ 点击确认提交    │
                    └────────┬────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ 检测发票号重复  │
                    └────────┬────────┘
                              │
              ┌───────────────┴───────────────┐
              │                               │
              ▼                               ▼
    ┌─────────────────┐             ┌─────────────────┐
    │  不重复        │             │  重复          │
    │ 进入待审批状态  │             │ 覆盖旧文件     │
    │                │             │ 更新记录       │
    └────────┬────────┘             └────────┬────────┘
              │                               │
              └───────────────┬───────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  会计审批       │
                    │ 批准/拒绝       │
                    └─────────────────┘
```

### 审批状态说明

| 状态值 | 显示文本 | 说明 | 可见范围 |
|--------|----------|------|----------|
| pending | 待审批 | 等待会计审批 | 仅会计端可见审批按钮 |
| approved | 已批准 | 审批通过 | 所有人可见 |
| rejected | 已拒绝 | 审批驳回 | 所有人可见 |

## 部署指南

### Docker 部署

#### 1. 环境准备

确保已安装 Docker 和 Docker Compose：

```bash
docker --version
docker-compose --version
```

#### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.docker .env

# 编辑 .env 文件，配置必要的环境变量
vim .env
```

**必须配置的环境变量：**

```env
LLM_API_KEY=your-api-key-here  # 必须填写，否则无法解析发票
```

#### 3. 启动服务

```bash
# 启动所有服务（后台运行）
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看服务日志
docker-compose logs -f
```

#### 4. 停止服务

```bash
docker-compose down
```

#### 5. 重新构建（代码更新后）

```bash
docker-compose up -d --build
```

### 手动部署

#### 后端部署

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
vim .env  # 填写 LLM_API_KEY

# 创建必要目录
mkdir -p source_files archives previews meta

# 启动服务
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### 前端部署

```bash
cd frontend

# 安装依赖
npm install

# 配置环境变量
cp .env.example .env
vim .env  # 如有需要修改 API 地址

# 构建生产版本
npm run build

# 使用 serve 或 nginx 提供静态文件服务
npx serve -s dist -l 80
```

### 数据持久化

以下目录/文件需要在部署时持久化存储：

| 路径 | 说明 | 重要性 |
|------|------|--------|
| backend/source_files | 源发票文件 | 高 |
| backend/archives | 归档发票文件 | 高 |
| backend/previews | 预览图 | 中 |
| backend/meta | 元信息文件 | 中 |
| backend/invoice.db | SQLite 数据库 | **极高** |

**Docker 部署数据持久化：**

```yaml
volumes:
  - ./backend/source_files:/app/source_files
  - ./backend/archives:/app/archives
  - ./backend/previews:/app/previews
  - ./backend/meta:/app/meta
  - ./backend/invoice.db:/app/invoice.db
```

## 目录结构说明

### 后端目录

| 目录 | 说明 |
|------|------|
| app/ | 应用核心代码 |
| source_files/ | 上传的原始 PDF 文件 |
| archives/ | 按规则命名的归档 PDF 文件 |
| previews/ | 发票首页预览 PNG 图片 |
| meta/ | JSON 格式的元数据信息 |
| invoice.db | SQLite 数据库文件 |

### 前端目录

| 目录 | 说明 |
|------|------|
| src/api/ | API 调用封装 |
| src/components/ | 可复用 Vue 组件 |
| src/views/ | 页面级组件 |
| src/types/ | TypeScript 类型定义 |
| dist/ | 生产构建输出 |

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
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**前端热更新：**
```bash
npm run dev -- --host 0.0.0.0 --port 5173
```

### Q4: 草稿和正式提交有什么区别？

| 特性 | 草稿模式 | 正式提交 |
|------|----------|----------|
| 去重检测 | 不检测 | 检测 |
| 状态 | draft | pending |
| 用途 | 修改信息后重新上传 | 提交审批 |

## 开发指南

### 代码规范

- **Python**: 遵循 PEP 8 规范
- **TypeScript**: 使用 ESLint + Prettier
- **Git 提交信息**: 使用 Conventional Commits 格式

### 本地开发

```bash
# 后端热重载
cd backend
python -m uvicorn app.main:app --reload

# 前端热更新
cd frontend
npm run dev
```

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
