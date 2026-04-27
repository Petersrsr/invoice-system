import json
import re

import httpx

from app.core.config import settings


JSON_PATTERN = re.compile(r"\{[\s\S]*\}")
# 企业主体背景：帮助模型更稳定理解发票上下文。
COMPANY_CONTEXT = (
    "企业报销主体信息如下：\n"
    "公司名称：上海矢吉信息科技有限公司\n"
    "开户银行：宁波银行股份有限公司上海徐汇支行\n"
    "开户账号：70030122000464825\n"
    "统一社会信用代码：91310120342086465C\n"
)


async def parse_invoice_with_llm(raw_text: str) -> dict:
    # 本地未配置密钥时返回空结构，便于前后端联调。
    if not settings.llm_api_key:
        return {
            "amount": None,
            "date": None,
            "seller_name": None,
            "purpose": None,
            "invoice_number": None,
            "tax_id": None,
            "_note": "LLM_API_KEY 未配置，返回空结果占位。",
        }

    url = f"{settings.llm_api_base.rstrip('/')}/v1/chat/completions"
    prompt = (
        "你是企业发票字段提取器。"
        "从发票文本中提取并且只返回 JSON，不要返回任何解释。"
        "字段为："
        "seller_name(销售方名称), purpose(用途分类，只能从以下枚举中选一个：食品/交通/住宿/办公/通信/培训/医疗/服务/设备/其他), amount(数字), "
        "invoice_number(发票号码), date(YYYY-MM-DD), tax_id(销售方税号)。"
        "无法确定请返回 null。\n"
        "以下是企业固定背景信息，请结合判断但不要输出额外字段：\n"
        f"{COMPANY_CONTEXT}\n"
        f"发票文本:\n{raw_text[:12000]}"
    )

    payload = {
        "model": settings.llm_model,
        "messages": [
            {"role": "system", "content": "你只返回 JSON，不要输出额外解释。"},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0,
    }
    headers = {
        "Authorization": f"Bearer {settings.llm_api_key}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()

        content = data["choices"][0]["message"]["content"]
        return _safe_parse_json(content)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"LLM API 调用失败: {str(e)}")
        return {
            "amount": None,
            "date": None,
            "seller_name": None,
            "purpose": None,
            "invoice_number": None,
            "tax_id": None,
            "_note": f"LLM API 调用失败: {str(e)}",
        }


def _safe_parse_json(content: str) -> dict:
    # 模型偶尔会返回带说明文本，尝试提取 JSON 片段兜底。
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        match = JSON_PATTERN.search(content)
        if not match:
            return {
                "amount": None,
                "date": None,
                "seller_name": None,
                "purpose": None,
                "invoice_number": None,
                "tax_id": None,
                "_note": "LLM 返回无法解析为 JSON",
            }
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return {
                "amount": None,
                "date": None,
                "seller_name": None,
                "purpose": None,
                "invoice_number": None,
                "tax_id": None,
                "_note": "LLM 返回 JSON 片段仍无法解析",
            }
