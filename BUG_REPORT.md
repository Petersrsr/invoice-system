# 全面 Bug 审查报告

> 检查日期：2026-04-30
> 审查范围：后端 (backend/app/) + 前端 (frontend/src/)

---

## 一、后端 Bug (20 个)

### 1. extract_text_from_pdf 资源泄漏 — Medium

- **文件**：`backend/app/services/pdf_parser.py:7-12`
- **问题**：`doc = fitz.open(...)` 后若 `page.get_text("text")` 抛异常，`doc.close()` 永远不会执行，文件句柄泄漏。对比 `render_pdf_first_page_to_png` 正确使用了 try/finally。
- **修复**：用 try/finally 包裹。

### 2. 空 PDF 崩溃 — Medium

- **文件**：`backend/app/services/pdf_parser.py:19`
- **问题**：`doc[0]` 在 PDF 为 0 页时抛 IndexError，无保护。
- **修复**：先检查 `len(doc) == 0`。

### 3. 上传损坏文件导致未捕获异常 — High

- **文件**：`backend/app/api/routes/invoices.py:55`
- **问题**：`extract_text_from_pdf(pdf_bytes)` 无 try/except。客户端可伪造 content-type，上传非 PDF 文件时 PyMuPDF 直接抛异常，返回 500 且无有意义的错误信息。
- **修复**：加 try/except，返回 400 + 友好提示；同时校验 PDF magic header (`%PDF`)。

### 4. 预览图生成失败时 meta 仍写入 URL — Medium

- **文件**：`backend/app/api/routes/invoices.py:106-122`
- **问题**：`render_pdf_first_page_to_png` 失败被 catch 后，`_write_meta` 仍无条件执行，写入不存在的预览文件名，前端拿到无效 URL。
- **修复**：仅在预览生成成功时才写入对应 URL。

### 5. file_name 为 None 时尝试删除目录 — Medium

- **文件**：`backend/app/api/routes/invoices.py:307-314`
- **问题**：`Path(settings.source_dir) / (source_file_name or "")` 当 `source_file_name` 为 None 时退化为目录本身，`unlink()` 会抛 IsADirectoryError。
- **修复**：跳过 None 文件名的清理。

### 6. 先删文件再提交数据库，非原子操作 — High

- **文件**：`backend/app/api/routes/invoices.py:278-285`
- **问题**：confirm_invoice 和 delete_invoice 中，`_cleanup_invoice_files` 先执行文件删除，再 `db.commit()`。若 commit 失败，文件已丢失但数据库记录仍在。
- **修复**：先 commit，再删文件；或用 try/finally 确保补偿。

### 7. confirm_invoice 两次 commit 非原子 — High

- **文件**：`backend/app/api/routes/invoices.py:281, 285`
- **问题**：第一次 commit 删除 duplicate，第二次 commit 设置 pending。中途崩溃导致数据不一致。
- **修复**：合并为一个事务。

### 8. 上传重复发票 TOCTOU 竞态 — High

- **文件**：`backend/app/api/routes/invoices.py:62-85`
- **问题**：`find_invoice_by_number` 与后续文件覆写/数据库更新不原子，并发上传同一发票号可互相覆盖文件。
- **修复**：用数据库锁或 SELECT FOR UPDATE + 事务包裹。

### 9. _normalize_purpose 逻辑错误 — Medium

- **文件**：`backend/app/services/invoice_service.py:276-286`
- **问题**：两个分支都返回 `"其他"`，LLM 返回的用途值被静默丢弃。
- **修复**：改为 `return purpose or "其他"`。

### 10. fallback 全表扫描 — Medium

- **文件**：`backend/app/services/invoice_service.py:92-94`
- **问题**：`find_invoice_by_number` 在列查询失败时加载全部记录到内存逐条正则匹配，性能隐患。
- **修复**：确保数据库表结构正确，消除 fallback；或加索引。

### 11. 每次请求创建新 AsyncOpenAI 客户端 — Medium

- **文件**：`backend/app/services/llm_client.py:42-46`
- **问题**：每次调用 `_get_client()` 创建新实例，连接池无法复用。
- **修复**：模块级单例。

### 12. LLM 错误信息泄露内部细节 — Medium

- **文件**：`backend/app/services/llm_client.py:70`
- **问题**：`f"LLM API 调用失败: {e}"` 直接包含异常原始信息（可能含主机名等），通过 `_note` 字段暴露给前端。
- **修复**：仅返回脱敏的通用错误消息，原始异常写日志。

### 13. 首次迁移回填逻辑不执行 — Low

- **文件**：`backend/app/main.py:37-38`
- **问题**：`if "approval_status" in existing` 仅在列已存在时为 True，首次添加列时跳过回填，旧记录 approval_status 为 NULL。
- **修复**：改为始终执行 `UPDATE ... WHERE approval_status IS NULL`。

### 14. SQL 字符串拼接模式 — Low

- **文件**：`backend/app/main.py:36`
- **问题**：DDL 中列名通过 f-string 拼接。当前值来自硬编码字典，但模式本身有 SQL 注入风险。
- **修复**：对列名做白名单校验。

### 15. content-type 由客户端提供，可伪造 — Medium

- **文件**：`backend/app/api/routes/invoices.py:48`
- **问题**：仅检查 `file.content_type`，非 PDF 文件伪造 Content-Type 即可绕过，结合 Bug 3 导致 500。
- **修复**：校验文件头前 4 字节是否为 `%PDF`。

### 16. _make_unique_file_name 循环无上限 — Low

- **文件**：`backend/app/services/invoice_service.py:237-248`
- **问题**：`while True` 无终止保证。
- **修复**：加合理上限或改用 UUID 后缀。

### 17. approve_invoice 无状态机检查 — Medium

- **文件**：`backend/app/api/routes/invoices.py:222-251`
- **问题**：draft 状态的发票可直接 approve（绕过 confirm），已 approved/rejected 的可重复审批。
- **修复**：检查当前 approval_status 是否允许目标转换。

### 18. _safe_parse_json 返回结构不一致 — Low

- **文件**：`backend/app/services/llm_client.py:73-100`
- **问题**：`_EMPTY_RESULT` 6 个 key，错误路径多一个 `_note` key。
- **修复**：统一结构。

### 19. invoice_date 存为 String — Low (设计)

- **文件**：`backend/app/db/models.py:19`
- **问题**：日期存为 `String(50)`，格式不统一，无法高效日期范围查询。
- **修复**：改为 Date 类型，迁移时格式标准化。

### 20. _normalize_invoice_number 大小写敏感 — Low

- **文件**：`backend/app/services/invoice_service.py:202-208`
- **问题**：只检查 `"null"` 和 `"None"`，不匹配小写 `"none"`。
- **修复**：`cleaned.lower() in {"未知号码", "null", "none", "n/a"}`

---

## 二、前端 Bug (13 个)

### 1. 快速上传时 setTimeout 状态覆盖 — Medium

- **文件**：`frontend/src/components/InvoiceUpload.vue:36-56`
- **问题**：上传成功后 setTimeout 3 秒重置状态，但未清理旧 timeout。3 秒内再次上传，旧 timeout 会覆盖新状态。
- **修复**：存 timeout ID，每次新上传前 clear，onBeforeUnmount 时也 clear。

### 2. 弹窗遮罩点击误删发票 — High

- **文件**：`frontend/src/views/EmployeePage.vue:60`
- **问题**：`@click.self="handleCancel"` 使点击遮罩层调用 `cancelInvoice`，用户仅想关闭弹窗却导致发票被永久删除。
- **修复**：遮罩点击改为仅关闭弹窗（不调用 cancel），取消操作只通过显式按钮触发。

### 3. loadData 无错误处理 — Medium

- **文件**：`frontend/src/views/AccountantPage.vue:75-77, 121`
- **问题**：`onMounted(loadData)` 无 try/catch，API 失败时 unhandled promise rejection，用户看到空列表无任何提示。
- **修复**：加 try/catch + 错误提示。

### 4. fetchInvoiceDetail 失败时显示旧数据 — Medium

- **文件**：`frontend/src/views/AccountantPage.vue:79-87`
- **问题**：`openDetail` 中若 fetch 失败，`selected.value` 保留上一次的值，弹窗渲染出另一张发票的详情。
- **修复**：失败时关闭弹窗或清空 selected。

### 5. confirmInvoice 返回类型错误 — Low

- **文件**：`frontend/src/api/invoice.ts:39`
- **问题**：返回类型标注为 `UploadInvoiceResponse`，应为状态对象。
- **修复**：更正类型。

### 6. confirmDeleteId 死代码 — Low

- **文件**：`frontend/src/components/InvoiceTable.vue:10, 25`
- **问题**：声明并重置但从未赋值非 null，实际使用 `window.confirm()`。
- **修复**：删除未使用的 ref。

### 7. 文件验证顺序错误 — Low

- **文件**：`frontend/src/components/InvoiceUpload.vue:28-34`
- **问题**：先检查大小再检查类型，非 PDF 大文件会提示"文件过大"而非"仅支持 PDF"。`!file` 检查为死代码。
- **修复**：先类型后大小；移除 `!file`。

### 8. API base URL 环境变量不一致 — Medium

- **文件**：`frontend/src/api/invoice.ts:20` vs `frontend/src/views/AccountantPage.vue:16`
- **问题**：使用不同环境变量名 `VITE_API_BASE` vs `VITE_API_ORIGIN`，部署者设一个另一个会 fallback 到不同默认值。
- **修复**：统一为同一个环境变量。

### 9. 无 404 路由 — Low

- **文件**：`frontend/src/router.ts`
- **问题**：未知路径渲染空白页。
- **修复**：加 catch-all 重定向到首页或 404 页。

### 10. 无全局 axios 错误拦截 — Medium

- **文件**：`frontend/src/api/invoice.ts:22-24`
- **问题**：axios 实例无 response interceptor，部分调用方未处理错误。
- **修复**：添加全局拦截器处理 401/500/网络错误。

### 11. 审批成功后刷新失败显示"审批失败" — Medium

- **文件**：`frontend/src/views/AccountantPage.vue:98-118`
- **问题**：`approveInvoice` 已成功，后续 `fetchInvoiceDetail` 或 `loadData` 失败时 catch 块显示"审批提交失败"，误导用户重试。
- **修复**：将审批调用单独 try/catch，后续刷新失败单独提示"刷新失败"。

### 12. closeDetail 未清空 selected — Low

- **文件**：`frontend/src/views/AccountantPage.vue:89-91`
- **问题**：关闭弹窗时 `selected.value` 保留旧值，再次打开时可能短暂显示旧数据。
- **修复**：`selected.value = null`。

### 13. 审批弹窗遮罩点击未检查 loading 状态 — Low

- **文件**：`frontend/src/views/AccountantPage.vue:305`
- **问题**：`approvalLoading` 为 true 时点击遮罩仍会关闭弹窗，但审批请求继续在后台执行。
- **修复**：loading 时禁用遮罩关闭。

---

## 三、汇总

| 严重度 | 后端 | 前端 | 合计 |
|--------|------|------|------|
| High | 5 | 2 | **7** |
| Medium | 9 | 7 | **16** |
| Low | 6 | 4 | **10** |
| **总计** | **20** | **13** | **33** |

### 优先修复建议

1. **数据一致性**：Bug B6、B7 — 先 commit 再删文件，合并事务
2. **并发安全**：Bug B8 — 上传重复发票加锁
3. **误操作防护**：Bug F2 — 遮罩点击不执行删除
4. **上传健壮性**：Bug B3 + B15 — PDF 校验 + 异常捕获
5. **用户体验**：Bug F3、F4、F11 — 错误处理与状态清理
