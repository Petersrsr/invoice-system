import json
import re

import httpx

from app.core.config import settings


JSON_PATTERN = re.compile(r"\{[\s\S]*\}")


async def parse_invoice_with_llm(raw_text: str) -> dict:
    if not settings.llm_api_key:
        return {
            "amount": None,
            "date": None,
            "title": None,
            "tax_id": None,
            "item_name": None,
            "_note": "LLM_API_KEY 未配置，返回空结果占位。",
        }

    url = f"{settings.llm_api_base.rstrip('/')}/v1/chat/completions"
    prompt = (
        "你是发票信息提取器。"
        "从以下文本提取字段并仅返回 JSON："
        "amount(数字), date(YYYY-MM-DD), title(抬头), tax_id(税号), item_name(品名)。"
        "无法确定请返回 null。\n\n"
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

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()

    content = data["choices"][0]["message"]["content"]
    return _safe_parse_json(content)


def _safe_parse_json(content: str) -> dict:
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        match = JSON_PATTERN.search(content)
        if not match:
            return {
                "amount": None,
                "date": None,
                "title": None,
                "tax_id": None,
                "item_name": None,
                "_note": "LLM 返回无法解析为 JSON",
            }
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return {
                "amount": None,
                "date": None,
                "title": None,
                "tax_id": None,
                "item_name": None,
                "_note": "LLM 返回 JSON 片段仍无法解析",
            }
