# 企业自动化发票报销系统

一个面向企业内部的自动化发票报销系统，支持发票上传、智能解析、归档管理和审批流程。

## 功能特性

- **发票上传**：支持拖拽上传 PDF 发票文件
- **智能解析**：使用 LLM 自动提取发票字段（金额、日期、抬头、税号、品名等）
- **自动归档**：按规则命名并存储源文件和归档文件
- **去重策略**：检测重复发票号，覆盖旧文件并更新记录
- **预览查看**：支持源文件下载、归档文件下载、预览图查看
- **审批流程**：发票审批状态管理（待审批/已批准/已拒绝）
- **统计报表**：发票数量、金额汇总、审批状态统计

## 技术栈

### 后端
- Python 3.11+
- FastAPI 0.100+
- SQLAlchemy 2.0+
- Pydantic 2.0+
- PyMuPDF (PDF 解析)
- httpx (HTTP 客户端)
- SQLite (数据库)

### 前端
- Vue 3 + Vite 5
- TypeScript
- Tailwind CSS 3
- Axios
- Vue Router

## 快速开始

### 环境要求

- Python 3.11+
- Node.js 20+
- npm 或 yarn

### 开发模式

#### 1. 克隆项目

```bash
git clone <repository-url>
cd invoice-system
```

#### 2. 后端启动

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 3. 前端启动

```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```

#### 4. 访问地址

- 前端：http://localhost:5173
- 后端 API：http://localhost:8000
- Swagger 文档：http://localhost:8000/docs

### Docker 部署（推荐）

#### 1. 配置环境变量

```bash
cp .env.docker .env
# 编辑 .env 文件，配置 LLM API Key
```

#### 2. 启动服务

```bash
docker-compose up -d
```

#### 3. 访问地址

- 前端：http://服务器IP
- 后端 API：http://服务器IP:8000

## 项目结构

```
invoice-system/
├── backend/                    # 后端服务
│   ├── app/                    # 应用代码
│   │   ├── main.py             # 入口文件
│   │   ├── core/               # 核心配置
│   │   │   └── config.py       # 配置管理
│   │   ├── db/                 # 数据库相关
│   │   │   ├── database.py     # 数据库连接
│   │   │   └── models.py       # 数据模型
│   │   ├── api/                # API 路由
│   │   │   └── routes/         # 路由定义
│   │   │       └── invoices.py # 发票相关 API
│   │   ├── schemas/            # Pydantic 模型
│   │   │   └── invoice.py      # 发票数据结构
│   │   └── services/           # 业务服务
│   │       ├── pdf_parser.py   # PDF 解析服务
│   │       ├── llm_client.py   # LLM 客户端
│   │       └── invoice_service.py # 发票业务逻辑
│   ├── requirements.txt         # Python 依赖
│   ├── Dockerfile              # 后端 Docker 配置
│   ├── invoice.db              # SQLite 数据库文件
│   ├── source_files/           # 源发票文件存储
│   ├── archives/               # 归档发票文件存储
│   ├── previews/               # 预览图存储
│   └── meta/                   # 元信息存储
├── frontend/                   # 前端应用
│   ├── src/                    # 源代码
│   │   ├── main.ts             # 入口文件
│   │   ├── App.vue             # 根组件
│   │   ├── router.ts           # 路由配置
│   │   ├── api/                # API 调用
│   │   │   └── invoice.ts      # 发票 API
│   │   ├── components/         # UI 组件
│   │   │   ├── InvoiceUpload.vue    # 上传组件
│   │   │   └── InvoiceTable.vue     # 表格组件
│   │   ├── views/              # 页面视图
│   │   │   ├── EmployeePage.vue     # 员工上传页
│   │   │   └── AccountantPage.vue   # 会计审批页
│   │   └── types/              # TypeScript 类型
│   │       └── invoice.ts      # 发票类型定义
│   ├── package.json            # npm 依赖
│   ├── Dockerfile              # 前端 Docker 配置
│   ├── nginx.conf              # Nginx 配置
│   └── vite.config.ts          # Vite 配置
├── docker-compose.yml          # Docker Compose 配置
├── .env.docker                 # Docker 环境变量模板
└── README.md                   # 项目说明文档
```

## API 接口文档

### 发票列表

- **GET** `/api/invoices`
- 获取发票列表

**查询参数：**
| 参数 | 类型 | 说明 |
|------|------|------|
| page | int | 页码，默认 0 |
| size | int | 每页数量，默认 20 |

**返回示例：**
```json
{
  "items": [
    {
      "id": 1,
      "file_name": "矢吉-上海罗森-食品-100.00元-12345678.pdf",
      "amount": 100.0,
      "invoice_date": "2026-04-01",
      "approval_status": "pending"
    }
  ],
  "total": 10,
  "page": 0,
  "size": 20
}
```

### 发票详情

- **GET** `/api/invoices/{invoice_id}`
- 获取单条发票详情

**返回示例：**
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
  "source_file_url": "/files/source/xxx.pdf",
  "archived_file_url": "/files/archive/xxx.pdf",
  "approval_status": "pending",
  "approval_comment": null,
  "approver_name": null,
  "approved_at": null
}
```

### 上传发票

- **POST** `/api/invoices/upload`
- 上传 PDF 发票文件

**请求体：** `multipart/form-data`

| 参数 | 类型 | 说明 |
|------|------|------|
| file | File | PDF 文件 |
| uploader_name | string | 上传人姓名（可选） |

**返回示例：**
```json
{
  "id": 1,
  "file_name": "矢吉-上海罗森-食品-100.00元-12345678.pdf",
  "invoice_number": "12345678",
  "amount": 100.0,
  "duplicate": false
}
```

### 审批发票

- **POST** `/api/invoices/{invoice_id}/approve`
- 审批发票（批准或拒绝）

**请求体：**
```json
{
  "status": "approved",
  "comment": "审批通过",
  "approver_name": "李四"
}
```

| 参数 | 类型 | 说明 |
|------|------|------|
| status | string | 审批状态：approved 或 rejected |
| comment | string | 审批备注（可选） |
| approver_name | string | 审批人姓名（必填） |

**返回示例：**
```json
{
  "id": 1,
  "approval_status": "approved",
  "approval_comment": "审批通过",
  "approver_name": "李四",
  "approved_at": "2026-04-27T10:00:00"
}
```

### 删除发票

- **DELETE** `/api/invoices/{invoice_id}`
- 删除发票记录及相关文件

### 健康检查

- **GET** `/health`
- 服务健康检查

**返回示例：**
```json
{
  "status": "ok"
}
```

## 环境变量配置

### 后端环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| APP_ENV | production | 运行环境 |
| LLM_API_BASE | https://api.deepseek.com | LLM API 地址 |
| LLM_API_KEY | - | LLM API Key（必填） |
| LLM_MODEL | deepseek-chat | LLM 模型名称 |
| DATABASE_URL | sqlite:///./invoice.db | 数据库连接地址 |

### 前端环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| VITE_API_ORIGIN | http://localhost:8000 | 后端 API 地址 |

## 数据库说明

### 发票记录表 (invoice_records)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| file_name | VARCHAR(255) | 归档文件名 |
| source_file_name | VARCHAR(255) | 源文件名 |
| archived_file_name | VARCHAR(255) | 归档文件名 |
| invoice_number | VARCHAR(128) | 发票号码 |
| uploader_name | VARCHAR(128) | 上传人姓名 |
| amount | FLOAT | 金额 |
| invoice_date | VARCHAR(50) | 发票日期 |
| title | VARCHAR(255) | 销售方名称 |
| tax_id | VARCHAR(64) | 税号 |
| item_name | VARCHAR(255) | 商品名称/用途 |
| raw_text | TEXT | 原始文本（审计用） |
| created_at | TIMESTAMP | 创建时间 |
| approval_status | VARCHAR(32) | 审批状态 |
| approval_comment | TEXT | 审批备注 |
| approver_name | VARCHAR(128) | 审批人 |
| approved_at | TIMESTAMP | 审批时间 |

## 发票归档命名规则

归档文件命名格式：

```
{公司简称}-{销售方名称}-{用途}-{金额}元-{发票号码}.pdf
```

示例：
```
矢吉-上海罗森便利有限公司-食品-100.00元-26317000000980499812.pdf
```

## 开发指南

### 代码规范

- Python：遵循 PEP 8 规范
- TypeScript：使用 ESLint 检查
- 提交信息：使用 Conventional Commits 格式

### 开发流程

1. 创建功能分支
2. 编写代码
3. 测试验证
4. 提交 PR

### 测试

```bash
# 后端测试（如有）
cd backend
python -m pytest

# 前端测试（如有）
cd frontend
npm test
```

## 部署指南

### Docker 部署

```bash
# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 重新构建
docker-compose up -d --build
```

### 手动部署

#### 后端

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### 前端

```bash
cd frontend
npm install
npm run build
npm run preview -- --host 0.0.0.0 --port 80
```

### 数据持久化

以下目录需要持久化存储：

- `backend/source_files` - 源发票文件
- `backend/archives` - 归档发票文件
- `backend/previews` - 预览图
- `backend/meta` - 元信息
- `backend/invoice.db` - SQLite 数据库

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 PR！