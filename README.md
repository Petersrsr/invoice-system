<div align="center">

# 📄 Invoice Automation System

**企业级发票自动化报销系统 — 上传、解析、归档、审批，一站搞定**

[![CI](https://github.com/user/invoice-system/actions/workflows/ci.yml/badge.svg)](https://github.com/user/invoice-system/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)

</div>

---

## ✨ 亮点

- 🤖 **AI 智能解析** — 上传 PDF 发票，LLM 自动提取金额、日期、销售方、税号等关键字段
- 📝 **草稿机制** — 先存草稿再确认，给用户二次检查的机会，避免错误提交
- 🔁 **智能去重** — 相同发票号自动覆盖旧记录，无需手动排查
- ✅ **审批工作流** — 待审批 → 批准/拒绝，三态流转清晰可控
- 📊 **统计看板** — 用途分布、金额排行、审批状态一目了然
- 🗂️ **自动归档** — 按 `公司-销售方-用途-金额-票号` 规则命名，告别手动整理

## 📸 截图

> _开发完成后可在这里添加系统截图_

## 🛠️ 技术栈

| 层 | 技术 |
|----|------|
| **前端** | Vue 3 · TypeScript · Vite 5 · Tailwind CSS 3 · Vue Router 4 |
| **后端** | Python 3.11+ · FastAPI · SQLAlchemy 2.0 · Pydantic |
| **解析** | PyMuPDF（PDF 提取） · DeepSeek LLM（字段识别） |
| **存储** | SQLite（零配置，开箱即用） |

## 🚀 快速开始

### 环境要求

| 依赖 | 版本 |
|------|------|
| Python | 3.11+ |
| Node.js | 20+ |

### 1. 克隆仓库

```bash
git clone https://github.com/user/invoice-system.git
cd invoice-system
```

### 2. 启动后端

```bash
cd backend

# 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env，填入你的 LLM API Key（必填）

# 启动服务
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. 启动前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev -- --host 0.0.0.0 --port 5173
```

### 4. 访问应用

| 服务 | 地址 |
|------|------|
| 🖥️ 前端界面 | http://localhost:5173 |
| 📡 后端 API | http://localhost:8000 |
| 📖 API 文档 | http://localhost:8000/docs |

> 💡 **首次使用**：打开前端后切换到「会计审批」页面，可查看统计看板和发票列表。

## 📋 功能一览

### 员工端（`/employee`）

- 拖拽或点击上传 PDF 发票
- 填写上传人姓名
- 上传后查看 AI 解析结果
- 确认提交或返回修改

### 会计端（`/accounting`）

- 📊 统计看板：发票数量、总金额、待审批数
- 📈 用途分布图 & 报销金额排行
- 📋 发票列表：支持查看详情、下载文件、预览 PDF
- ✅ 审批操作：批准/拒绝 + 备注
- 🗑️ 删除功能：彻底清理数据库与文件

### 业务流程

```
员工上传 PDF → AI 解析字段 → 保存草稿 → 员工确认提交
                                          ↓
                                  检测发票号是否重复
                                    ↓           ↓
                                 新发票      重复发票
                                    ↓           ↓
                                进入审批    覆盖旧记录
                                    ↓
                            会计审批（批准/拒绝）
```

## 🔌 API 接口

<details>
<summary><b>点击查看完整 API 文档</b></summary>

### 基础信息

| 项目 | 值 |
|------|------|
| Base URL | `/api/invoices` |
| 认证 | 无（内网 MVP 阶段） |

### 接口列表

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/invoices/upload` | 上传发票（支持草稿模式） |
| `GET` | `/api/invoices` | 获取发票列表 |
| `GET` | `/api/invoices/{id}` | 获取发票详情 |
| `POST` | `/api/invoices/{id}/confirm` | 确认提交草稿 |
| `DELETE` | `/api/invoices/{id}/cancel` | 取消并删除草稿 |
| `POST` | `/api/invoices/{id}/approve` | 审批发票 |
| `DELETE` | `/api/invoices/{id}/delete` | 彻底删除发票 |
| `GET` | `/health` | 健康检查 |

### 上传发票示例

```bash
curl -X POST http://localhost:8000/api/invoices/upload \
  -F "file=@invoice.pdf" \
  -F "uploader_name=张三" \
  -F "draft=true"
```

响应：

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

</details>

## 📂 项目结构

```
invoice-system/
├── backend/                      # 后端 FastAPI 服务
│   ├── app/
│   │   ├── main.py               # 应用入口
│   │   ├── core/config.py        # 环境变量配置
│   │   ├── db/                   # 数据库模型 & 连接
│   │   ├── api/routes/           # API 路由
│   │   ├── schemas/              # Pydantic 数据模型
│   │   └── services/             # 业务逻辑
│   │       ├── invoice_service.py # 发票核心逻辑
│   │       ├── llm_client.py     # LLM 调用封装
│   │       └── pdf_parser.py     # PDF 文本/图片提取
│   ├── source_files/             # 上传的源 PDF 文件
│   ├── archives/                 # 归档后的发票文件
│   ├── previews/                 # PDF 预览图（PNG）
│   ├── meta/                     # 文件元数据（JSON）
│   └── requirements.txt
├── frontend/                     # 前端 Vue 应用
│   ├── src/
│   │   ├── api/                  # API 调用封装
│   │   ├── components/           # 可复用组件
│   │   ├── views/                # 页面视图
│   │   └── types/                # TypeScript 类型定义
│   └── package.json
├── deploy/                       # 部署脚本 & systemd 服务
├── .github/workflows/ci.yml      # CI 流水线
└── DEPLOYMENT.md                 # 生产部署指南
```

## ⚙️ 环境变量

### 后端 `backend/.env`

| 变量 | 默认值 | 必填 | 说明 |
|------|--------|------|------|
| `LLM_API_KEY` | — | **✅** | LLM API 密钥（如 [DeepSeek](https://platform.deepseek.com/)） |
| `LLM_API_BASE` | `https://api.deepseek.com` | 否 | LLM API 地址 |
| `LLM_MODEL` | `deepseek-chat` | 否 | 模型名称 |
| `DATABASE_URL` | `sqlite:///./invoice.db` | 否 | 数据库连接 |

### 前端 `frontend/.env`（通常不需要修改）

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `VITE_API_BASE` | 自动检测 | 后端 API 地址 |

## 🗃️ 数据库

使用 SQLite，**零配置开箱即用**。启动时自动创建表和索引，无需手动迁移。

<details>
<summary><b>发票记录表字段说明</b></summary>

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | INTEGER | 主键 |
| `file_name` | VARCHAR(255) | 归档文件名 |
| `source_file_name` | VARCHAR(255) | 源文件名 |
| `archived_file_name` | VARCHAR(255) | 归档文件名 |
| `invoice_number` | VARCHAR(128) | 发票号码 |
| `uploader_name` | VARCHAR(128) | 上传人 |
| `amount` | FLOAT | 金额 |
| `invoice_date` | VARCHAR(50) | 发票日期 |
| `title` | VARCHAR(255) | 销售方名称 |
| `tax_id` | VARCHAR(64) | 税号 |
| `item_name` | VARCHAR(255) | 商品名称 |
| `raw_text` | TEXT | 原始文本 |
| `created_at` | TIMESTAMP | 创建时间 |
| `approval_status` | VARCHAR(32) | 审批状态 |
| `approval_comment` | TEXT | 审批备注 |
| `approver_name` | VARCHAR(128) | 审批人 |
| `approved_at` | TIMESTAMP | 审批时间 |

</details>

## 🚢 生产部署

支持 systemd 守护进程部署，详见 [DEPLOYMENT.md](./DEPLOYMENT.md)。

```bash
# 快速启动（开发模式）
cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
cd frontend && npm run dev -- --host 0.0.0.0 --port 5173

# 生产模式
cd frontend && npm run build && npx serve -s dist -l 80
cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 🤝 参与贡献

欢迎任何形式的贡献！

1. Fork 本仓库
2. 创建功能分支：`git checkout -b feature/awesome-feature`
3. 提交更改：`git commit -m 'feat: add awesome feature'`
4. 推送分支：`git push origin feature/awesome-feature`
5. 提交 Pull Request

### 开发规范

- **Python**：遵循 [PEP 8](https://peps.python.org/pep-0008/)
- **TypeScript/Vue**：使用 Composition API + `<script setup>` 语法
- **提交信息**：采用 [Conventional Commits](https://www.conventionalcommits.org/) 格式

## ❓ FAQ

**Q: 上传发票解析失败怎么办？**
A: 检查 `backend/.env` 中的 `LLM_API_KEY` 是否正确配置。未配置 LLM 时系统仍可上传文件，但不会自动提取字段。

**Q: 支持哪些格式的发票？**
A: 目前仅支持 PDF 格式，单个文件最大 10MB。

**Q: 草稿和正式提交有什么区别？**
A: 草稿不触发重复检测，可以随时修改后重新上传；确认提交后进入审批流程，此时相同发票号会自动覆盖旧记录。

**Q: 可以替换 LLM 服务吗？**
A: 可以。只需修改 `LLM_API_BASE` 和 `LLM_MODEL` 配置，适配任何兼容 OpenAI API 格式的服务（如 OpenAI、通义千问、Ollama 本地模型等）。

## 📄 许可证

本项目基于 [MIT License](./LICENSE) 开源。
