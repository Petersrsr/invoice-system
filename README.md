# 企业自动化发票报销系统（MVP）交接文档

一个面向企业内部的自动化发票报销系统：上传 PDF 后自动提取字段、完成归档与入库，并在前端列表/详情页可追溯查看。

## 1. 项目背景（最初需求）

本项目最初需求如下（保留原意）：

- 开发企业内部自动化发票报销系统。
- 后端：Python FastAPI，集成 PDF 解析（PyMuPDF）并调用外部大模型 API（DeepSeek/Claude 兼容 Chat Completions）。
- 前端：Vue3（Vite）+ Tailwind CSS，极简风格。
- 数据库：SQLite（MVP 阶段）。
- 核心流：
  - 用户页：大拖拽上传框，支持 PDF。
  - 链路：上传 -> PDF 文本提取 -> LLM 解析（金额/日期/抬头/税号/品名等）-> JSON。
  - 管理页：会计查看解析后的汇总列表。

## 2. 当前实现范围

已完成能力：

- PDF 上传与后端解析链路。
- LLM 字段提取 + 正则兜底修正。
- 发票归档命名：`矢吉-{销售方名称}-{用途}-{金额}元-{发票号码}.pdf`。
- 源文件与归档文件双落盘。
- 发票详情页支持：
  - 源文件下载。
  - 归档文件下载。
  - 源发票预览图（首张）。
  - 归档发票预览图（首张）。
- 审计留存目录：`source_files`、`archives`、`previews`、`meta`。
- 发票号去重策略：检测重复时覆盖旧文件并更新原记录，前端弹窗提示。
- 提供 `systemd` 常驻部署文件，服务监听 `0.0.0.0`。

## 3. 技术栈

- 后端：FastAPI + SQLAlchemy + Pydantic + PyMuPDF + httpx
- 前端：Vue3 + Vite + TypeScript + Tailwind CSS + Axios
- 存储：SQLite（`backend/invoice.db`）

## 4. 目录结构（关键路径）

```text
invoice-system/
├─ backend/
│  ├─ app/
│  │  ├─ main.py
│  │  ├─ core/config.py
│  │  ├─ db/
│  │  │  ├─ database.py
│  │  │  └─ models.py
│  │  ├─ api/routes/invoices.py
│  │  ├─ schemas/invoice.py
│  │  └─ services/
│  │     ├─ pdf_parser.py
│  │     ├─ llm_client.py
│  │     └─ invoice_service.py
│  ├─ requirements.txt
│  ├─ .env.example
│  ├─ invoice.db
│  ├─ source_files/   # 源发票
│  ├─ archives/       # 归档发票
│  ├─ previews/       # 预览图
│  └─ meta/           # 预览元信息
├─ frontend/
│  ├─ src/
│  │  ├─ App.vue
│  │  ├─ api/invoice.ts
│  │  ├─ components/InvoiceUpload.vue
│  │  ├─ components/InvoiceTable.vue
│  │  ├─ types/invoice.ts
│  │  └─ env.d.ts
│  ├─ package.json
│  └─ .env.example
└─ deploy/
   ├─ start_backend.sh
   ├─ start_frontend.sh
   └─ systemd/
      ├─ invoice-backend.service
      └─ invoice-frontend.service
```
└─ scripts/
   └─ clean_test_data.sh


## 5. 核心业务流程

1. 前端上传 PDF 到 `POST /api/invoices/upload`。
2. 后端 `pdf_parser.extract_text_from_pdf()` 提取全文文本。
3. `llm_client.parse_invoice_with_llm()` 请求外部模型，尝试返回 JSON 字段。
4. `invoice_service.normalize_extracted_fields()` 使用规则兜底（日期、发票号、金额、用途归类）。
5. 去重判断：
   - 若 `invoice_number` 命中已有记录：覆盖旧源文件/归档文件，更新原记录。
   - 若未命中：创建新记录并写入新文件。
6. 生成预览图（首张）并写入 `meta/{id}.json`。
7. 前端列表展示汇总，点击行进入详情并查看文件链接与预览图。

## 6. 去重策略（当前行为）

- 判定键：发票号 `invoice_number`。
- 命中后行为：覆盖旧文件 + 更新旧记录（不新增记录）。
- 前端反馈：显示并弹窗 `检测到重复发票号，已覆盖旧文件并更新记录`。

注意：

- 如果 LLM 错提取了发票号，可能出现“误判重复”。这是当前设计已知风险，建议后续升级为复合键策略（如 `发票号 + 税号`）。

## 7. API 说明（MVP）

### 7.1 上传发票

- `POST /api/invoices/upload`
- `multipart/form-data` 字段：`file`
- 仅支持：`application/pdf` / `application/x-pdf`

成功返回（示例）：

```json
{
  "id": 11,
  "file_name": "矢吉-上海恭汇贸易有限公司-食品-27.80元-26312000002361255451.pdf",
  "replaced": true,
  "message": "检测到重复发票号，已覆盖旧文件并更新记录",
  "extracted": {
    "amount": 27.8,
    "date": "2026-04-17",
    "seller_name": "上海恭汇贸易有限公司",
    "purpose": "食品",
    "invoice_number": "26312000002361255451",
    "tax_id": "913101097927991127",
    "title": "上海恭汇贸易有限公司",
    "item_name": "食品"
  }
}
```

### 7.2 发票列表

- `GET /api/invoices`
- 返回按 `id desc` 排序。

### 7.3 发票详情

- `GET /api/invoices/{invoice_id}`
- 返回基础字段 + 文件链接 + 预览图链接：
  - `source_file_url`
  - `archived_file_url`
  - `source_preview_image_url`
  - `archive_preview_image_url`

### 7.4 健康检查

- `GET /health` -> `{"status":"ok"}`

## 8. 环境变量

### 8.1 后端 `backend/.env`

参考 `backend/.env.example`：

```env
APP_NAME=Invoice Reimbursement API
APP_ENV=dev
LLM_API_BASE=https://api.deepseek.com
LLM_API_KEY=your-api-key
LLM_MODEL=deepseek-chat
DATABASE_URL=sqlite:///./invoice.db
ARCHIVE_DIR=./archives
SOURCE_DIR=./source_files
PREVIEW_DIR=./previews
META_DIR=./meta
```

### 8.2 前端 `frontend/.env`

参考 `frontend/.env.example`：

```env
VITE_API_BASE=http://127.0.0.1:8000/api
VITE_API_ORIGIN=http://127.0.0.1:8000
```

## 9. 本地开发（推荐流程）

### 9.1 后端

```bash
cd /www/wwwroot/invoice-system/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 9.2 前端

```bash
cd /www/wwwroot/invoice-system/frontend
npm install
cp .env.example .env
npm run dev -- --host 0.0.0.0 --port 5173
```

### 9.3 开发校验

```bash
# backend
cd /www/wwwroot/invoice-system/backend
python3 -m compileall app

# frontend
cd /www/wwwroot/invoice-system/frontend
npx tsc --noEmit
npm run build
```

## 10. 生产部署（systemd 常驻）

仓库内已提供：

- `deploy/start_backend.sh`
- `deploy/start_frontend.sh`
- `deploy/systemd/invoice-backend.service`
- `deploy/systemd/invoice-frontend.service`

安装：

```bash
sudo cp /www/wwwroot/invoice-system/deploy/systemd/invoice-backend.service /etc/systemd/system/
sudo cp /www/wwwroot/invoice-system/deploy/systemd/invoice-frontend.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now invoice-backend
sudo systemctl enable --now invoice-frontend
```

状态与日志：

```bash
sudo systemctl status invoice-backend
sudo systemctl status invoice-frontend
sudo journalctl -u invoice-backend -f
sudo journalctl -u invoice-frontend -f
```

端口约定：

- 后端：`0.0.0.0:8000`
- 前端预览：`0.0.0.0:4173`（如使用 `npm run dev`，通常为 `5173`）

## 11. 数据与文件说明

- SQLite：`backend/invoice.db`
- 发票主表：`invoice_records`
- 关键字段：
  - `id`
  - `file_name`
  - `source_file_name`
  - `archived_file_name`
  - `invoice_number`
  - `amount`
  - `invoice_date`
  - `title`
  - `tax_id`
  - `item_name`
  - `raw_text`
  - `created_at`

说明：

- `main.py` 启动时会自动检查并补齐历史 SQLite 缺失列（兼容旧库）。

## 12. 常见问题排查

### 12.1 上传失败，前端提示“检查后端或 API Key”

优先检查：

- `LLM_API_KEY`、`LLM_API_BASE`、`LLM_MODEL` 是否有效。
- 后端日志是否出现：
  - LLM 请求失败（4xx/5xx/超时）。
  - SQLite 列缺失或写入失败。
  - PDF 解析异常。

### 12.2 明明新文件却提示“重复发票号”

原因：

- 去重按“发票号”而非“文件名”判定。
- 文件名不同但发票号相同，仍会覆盖更新。
- 若 LLM 提取发票号错误，可能误判。

### 12.3 预览图为空

检查：

- `backend/previews/`、`backend/meta/` 是否可写。
- 上传文件是否为有效 PDF（有可渲染首页）。

### 12.4 后端起不来 / 端口占用

检查：

- `ss -ltnp | grep 8000`
- `sudo journalctl -u invoice-backend -n 200`

## 13. 测试数据一键清理

适用场景：

- 联调或验收后，需要清空测试产生的发票文件与数据库记录。

脚本位置：

- `scripts/clean_test_data.sh`

执行方式：

```bash
cd /www/wwwroot/invoice-system
./scripts/clean_test_data.sh
```

脚本行为（幂等，可重复执行）：

- 清空 `backend/previews/` 下所有文件。
- 清空 `backend/source_files/` 下所有文件。
- 清空 `backend/archives/` 下所有文件。
- 清空 `backend/meta/` 下所有文件。
- 清空数据库 `backend/invoice.db` 的 `invoice_records` 表数据。

注意事项：

- 该脚本会删除所有已上传发票相关文件与记录，请勿在正式生产数据上误执行。
- 建议执行前先备份数据库：

```bash
cp /www/wwwroot/invoice-system/backend/invoice.db /www/wwwroot/invoice-system/backend/invoice.db.bak.$(date +%F-%H%M%S)
```

## 14. 安全与合规注意事项

当前状态（MVP）：

- CORS 仍是全开放配置，生产建议收敛白名单。
- 尚无鉴权和权限分级。
- LLM 请求与发票原文可能包含敏感信息，建议增加脱敏与审计策略。

至少应补充：

- API 鉴权（如 JWT / 内网网关鉴权）。
- 访问日志与操作审计日志。
- 反向代理限流与上传大小限制。

## 15. 接手开发建议（下一步优先级）

1. 稳定性：为上传链路添加统一异常处理与错误码映射。
2. 精准去重：将去重键升级为复合条件（如 `发票号 + 税号`）。
3. 安全：收紧 CORS、增加鉴权、限制静态文件访问策略。
4. 测试：补齐 `tests/`（上传、去重、详情、预览、异常分支）。
5. 可维护性：引入 Alembic 管理数据库迁移，替代启动时手工补列。

## 16. 快速接手清单（新同学）

1. 阅读：`backend/app/api/routes/invoices.py`
2. 阅读：`backend/app/services/invoice_service.py`
3. 阅读：`backend/app/services/llm_client.py`
4. 启动本地前后端并上传一张样例 PDF 验证全链路。
5. 确认 `source_files/archives/previews/meta` 四个目录有写权限。
6. 执行 `npx tsc --noEmit` 与 `npm run build`，确保前端构建通过。
7. 测试结束后执行 `./scripts/clean_test_data.sh` 清理测试数据。
