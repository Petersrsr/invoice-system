# 企业自动化发票报销系统 - 项目规则

## 重要提醒

### 1. 全局考虑问题
- **重要**：修改代码时必须考虑全局影响，不要只修改局部
- **重要**：修改代码后必须更新进程，不要让用户手动重启
  - 后端：使用 `--reload` 参数启动，实现代码热重载
  - 前端：使用 `npm run dev`，默认启用热更新

### 2. 功能开发原则
- **重要**：一次性完成功能，避免分多次对话
- 在实现功能前，先全面分析需求，考虑所有相关文件和组件
- 涉及前后端的功能，同时更新两端代码

## 项目部署信息

### 开发模式启动

#### 后端
```bash
cd /www/wwwroot/invoice-system/backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 前端
```bash
cd /www/wwwroot/invoice-system/frontend
npm run dev -- --host 0.0.0.0 --port 5173
```

### 生产模式部署

#### Docker 部署
```bash
cd /www/wwwroot/invoice-system
docker-compose up -d
```

#### 手动部署
- 前端端口：80
- 后端端口：8000

### 局域网访问配置
- **重要**：服务必须绑定到 `0.0.0.0`，不能是 `127.0.0.1`
- 防火墙需要关闭或放行对应端口（80、8000、5173）

## 核心业务逻辑

### 草稿机制
- 上传发票时默认为草稿模式（`draft=true`）
- 草稿模式**不触发**去重检测
- 草稿可以修改后重新上传
- 确认提交后才进行去重检测

### 去重策略
- 仅在正式提交（confirm）时检测发票号重复
- 检测到重复时自动覆盖旧文件并更新记录
- 返回 `replaced: true` 表示已覆盖

### 审批流程
- 三种状态：`pending`（待审批）、`approved`（已批准）、`rejected`（已拒绝）
- 默认状态：`pending`
- 只有待审批状态的发票才显示审批按钮

### 删除功能
- 删除发票时同时删除：
  - 数据库记录
  - 源文件（source_files/）
  - 归档文件（archives/）
  - 预览图（previews/）
  - 元数据文件（meta/）
- 需要用户确认后才执行删除

## 环境变量配置

### 后端（backend/.env）
```
LLM_API_KEY=your-api-key-here  # 必填，否则无法解析发票
LLM_API_BASE=https://api.deepseek.com
LLM_MODEL=deepseek-chat
DATABASE_URL=sqlite:///./invoice.db
```

### 前端（frontend/.env）
```
VITE_API_BASE=http://localhost:8000/api
```

## API 端点

### 发票相关
- `POST /api/invoices/upload` - 上传发票
- `GET /api/invoices` - 获取发票列表
- `GET /api/invoices/{id}` - 获取发票详情
- `POST /api/invoices/{id}/confirm` - 确认提交草稿
- `DELETE /api/invoices/{id}/cancel` - 取消并删除草稿
- `POST /api/invoices/{id}/approve` - 审批发票
- `DELETE /api/invoices/{id}/delete` - 彻底删除发票

### 静态文件
- `/files/source/` - 源文件
- `/files/archive/` - 归档文件
- `/files/preview/` - 预览图

## 数据库结构

### invoice_records 表关键字段
- `id` - 主键
- `invoice_number` - 发票号码（已建索引）
- `approval_status` - 审批状态（pending/approved/rejected）
- `uploader_name` - 上传人姓名
- `amount` - 金额
- `invoice_date` - 发票日期
- `created_at` - 创建时间

## 页面路由

- `/` - 员工上传页（EmployeePage.vue）
- `/accountant` - 会计审批页（AccountantPage.vue）

## 代码规范

### Python
- 遵循 PEP 8 规范
- 使用 SQLAlchemy ORM
- 使用 Pydantic 进行数据验证

### TypeScript/Vue
- 使用 TypeScript 类型定义
- 遵循 Vue 3 Composition API 风格
- 使用 Tailwind CSS 进行样式设计

## 常见问题

### 上传失败
- 检查 LLM_API_KEY 是否配置
- 检查后端服务是否正常运行
- 查看后端日志获取详细错误信息

### 局域网无法访问
- 确保服务绑定到 0.0.0.0
- 检查防火墙设置
- 确认端口是否正确（80、8000、5173）

### 审批状态默认为已拒绝
- 检查数据库中 approval_status 字段的默认值
- 确保新记录默认为 'pending'

## 文件路径

### 后端
- `/www/wwwroot/invoice-system/backend/`
- 数据库：`backend/invoice.db`
- 源文件：`backend/source_files/`
- 归档文件：`backend/archives/`
- 预览图：`backend/previews/`
- 元数据：`backend/meta/`

### 前端
- `/www/wwwroot/invoice-system/frontend/`
- 构建输出：`frontend/dist/`
- 源代码：`frontend/src/`

## 开发注意事项

1. **每次修改代码后，确保进程已更新**
   - 后端：使用 `--reload` 参数
   - 前端：使用 `npm run dev`

2. **添加功能时一次性完成**
   - 分析所有相关文件
   - 同时更新前后端代码
   - 测试完整流程

3. **考虑全局影响**
   - 修改一个功能时，检查是否影响其他功能
   - 确保数据库结构变更向后兼容
   - 保持 API 接口一致性
