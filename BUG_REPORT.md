# 企业自动化发票报销系统 - Bug 检查报告

> 检查日期：2026-04-30
> 修复日期：2026-04-30

## 🔴 严重 Bug

### Bug 1：cancel 接口没有清理关联文件 ✅ 已修复

- **位置**：`backend/app/api/routes/invoices.py` → `cancel_invoice` 函数
- **问题**：`DELETE /{id}/cancel` 只删除了数据库记录，没有像 `delete` 接口那样清理 `source_files`、`archives`、`previews`、`meta` 目录中的关联文件。导致磁盘文件泄漏。
- **影响**：草稿取消后文件残留在磁盘上。
- **修复方式**：抽取 `_cleanup_invoice_files` 公共函数，cancel 和 delete 共用。

### Bug 2：cancel 接口对已提交发票也会直接删除，没有状态校验 ✅ 已修复

- **位置**：`backend/app/api/routes/invoices.py` → `cancel_invoice` 函数
- **问题**：cancel 路由没有检查 `approval_status`，任何状态的发票（包括已批准的）都可以被取消删除。
- **影响**：已审批通过的发票可被员工通过调用 cancel 接口删除，破坏审批流程。
- **修复方式**：添加 `approval_status != "draft"` 校验，仅允许草稿状态取消。

### Bug 3：confirm 接口没有去重检测 ✅ 已修复

- **位置**：`backend/app/api/routes/invoices.py` → `confirm_invoice` 函数
- **问题**：`POST /{id}/confirm` 只是把 `approval_status` 设为 `"pending"`，但没有进行发票号去重检测。根据项目规则："草稿模式不触发去重检测，确认提交时才检测"——但当前 confirm 实现完全没有去重逻辑。
- **影响**：两张相同发票号的草稿都被确认提交时不会触发覆盖机制，导致数据重复。
- **修复方式**：confirm 接口中添加发票号去重逻辑，发现重复时清理旧记录文件并删除旧记录。

### Bug 4：upload 接口的 draft 参数没有实际区分草稿状态 ✅ 已修复

- **位置**：`backend/app/api/routes/invoices.py` → `upload_invoice` 函数
- **问题**：上传时虽然 `draft=True` 跳过了去重检测，但最终保存的记录 `approval_status` 默认值仍为 `"pending"`，并没有标记为草稿（如 `"draft"` 状态）。
- **影响**：草稿和已提交的发票在数据库中无法区分。
- **修复方式**：`save_invoice_with_files` 新增 `approval_status` 参数，上传路由根据 `draft` 参数传入 `"draft"` 或 `"pending"`。前端类型同步更新。

### Bug 5：EmployeePage.vue 确认弹窗按钮没有实际调用后端接口 ✅ 已修复

- **位置**：`frontend/src/views/EmployeePage.vue` → `closeConfirm` 函数
- **问题**：`closeConfirm` 函数只是关闭了弹窗，没有调用后端的 `confirmInvoice(id)` 接口来确认提交草稿。同样"返回修改"也没有调用 `cancelInvoice(id)` 来取消草稿。
- **影响**：草稿机制完全失效，上传后记录永远停留在默认 `pending` 状态。
- **修复方式**：新增 `handleConfirm` 和 `handleCancel` 函数，分别调用 `confirmInvoice` 和 `cancelInvoice` API，按钮添加 loading 状态。

## 🟡 中等 Bug

### Bug 6：approved_at 使用 datetime.utcnow() 而非带时区的时间 ✅ 已修复

- **位置**：`backend/app/api/routes/invoices.py` → `approve_invoice` 函数
- **问题**：`datetime.utcnow()` 生成无时区的 UTC 时间，但模型定义为 `DateTime(timezone=True)`，与 `created_at` 的 `server_default=func.now()` 时区处理不统一。
- **影响**：审批时间可能与创建时间显示有时差。
- **修复方式**：改用 `datetime.now(timezone.utc)` 生成带时区的 UTC 时间。

### Bug 7：_sanitize_filename_part 去除所有空白字符过于激进 ✅ 已修复

- **位置**：`backend/app/services/invoice_service.py` → `_sanitize_filename_part` 函数
- **问题**：`re.sub(r"\s+", "", text)` 会删除所有空白字符，包括有意义的空格。
- **影响**：文件名中原本有意义的空格被移除。
- **修复方式**：改为 `re.sub(r"\s+", " ", text).strip()`，保留单词间的单个空格。

### Bug 8：cancel 和 delete 接口重复代码 ✅ 已修复

- **位置**：`backend/app/api/routes/invoices.py` → `cancel_invoice`、`delete_invoice`
- **问题**：两个接口各自实现文件清理逻辑，代码重复。
- **影响**：维护成本高，修改一处容易遗漏另一处。
- **修复方式**：抽取 `_cleanup_invoice_files` 公共函数统一复用。

## 🟢 低级问题

### Bug 9：InvoiceRecord 模型字段命名与业务语义不一致

- **位置**：`backend/app/db/models.py`
- **问题**：数据库用 `title` 存储销售方名称、用 `item_name` 存储用途分类，后端代码中到处需要做 `title ↔ seller_name`、`item_name ↔ purpose` 的转换，极易混淆。
- **影响**：代码可读性差，维护风险高。（本次不修改，涉及面太广）
- **状态**：已知，暂不修复 ⏭️

### Bug 10：前端 confirmInvoice 和 cancelInvoice 已定义但从未使用 ✅ 已修复

- **位置**：`frontend/src/api/invoice.ts` → `confirmInvoice`、`cancelInvoice`
- **问题**：两个 API 函数已经定义，但在页面组件中完全没有被调用。
- **影响**：草稿确认/取消的流程只做了一半。
- **修复方式**：随 Bug 5 一起修复，EmployeePage.vue 已接入这两个 API。
