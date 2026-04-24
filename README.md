# 企业自动化发票报销系统（MVP）

## 项目结构

```text
invoice-system/
  backend/
    app/
      api/routes/invoices.py
      core/config.py
      db/database.py
      db/models.py
      schemas/invoice.py
      services/pdf_parser.py
      services/llm_client.py
      services/invoice_service.py
      main.py
    requirements.txt
    .env.example
  frontend/
    src/
      api/invoice.ts
      components/InvoiceUpload.vue
      components/InvoiceTable.vue
      types/invoice.ts
      App.vue
      main.ts
      style.css
    index.html
    package.json
    tailwind.config.js
    postcss.config.js
    vite.config.ts
  README.md
```

## 后端启动

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

## 前端启动

```bash
cd frontend
npm install
npm run dev
```

## 核心流程

1. 用户上传 PDF 发票。
2. FastAPI 使用 PyMuPDF 提取文本。
3. 文本发送给 DeepSeek/Claude 兼容的 Chat Completions API。
4. 返回结构化 JSON 并写入 SQLite。
5. 会计页面展示全部解析记录。
