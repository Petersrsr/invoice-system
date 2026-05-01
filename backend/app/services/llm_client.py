import json
import logging
import re

from openai import AsyncOpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)

JSON_PATTERN = re.compile(r"\{[\s\S]*\}")
_client: AsyncOpenAI | None = None
COMPANY_CONTEXT = (
    "企业报销主体信息如下：\n"
    "公司名称：上海矢吉信息科技有限公司\n"
    "开户银行：宁波银行股份有限公司上海徐汇支行\n"
    "开户账号：70030122000464825\n"
    "统一社会信用代码：91310120342086465C\n"
)

_PROMPT_TEMPLATE = (
    "你是企业发票字段提取器。"
    "从发票文本中提取并且只返回 JSON，不要返回任何解释。"
    "字段为："
    "seller_name(销售方名称), purpose(用途分类，只能从以下枚举中选一个：食品/交通/住宿/办公/通信/培训/医疗/服务/设备/其他), amount(数字), "
    "invoice_number(发票号码), date(YYYY-MM-DD), tax_id(销售方税号)。"
    "无法确定请返回 null。\n"
    "以下是企业固定背景信息，请结合判断但不要输出额外字段：\n"
    "{company_context}\n"
    "发票文本:\n{raw_text}"
)

_EMPTY_RESULT = {
    "amount": None,
    "date": None,
    "seller_name": None,
    "purpose": None,
    "invoice_number": None,
    "tax_id": None,
}


def _get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        base_url = settings.llm_api_base.rstrip("/")
        if not base_url.endswith("/v1"):
            base_url = f"{base_url}/v1"
        _client = AsyncOpenAI(api_key=settings.llm_api_key, base_url=base_url)
    return _client


async def parse_invoice_with_llm(raw_text: str) -> dict:
    if not settings.llm_api_key:
        return {**_EMPTY_RESULT, "_note": "LLM_API_KEY 未配置，返回空结果占位。"}

    client = _get_client()
    prompt = _PROMPT_TEMPLATE.format(company_context=COMPANY_CONTEXT, raw_text=raw_text[:12000])

    try:
        resp = await client.chat.completions.create(
            model=settings.llm_model,
            messages=[
                {"role": "system", "content": "你只返回 JSON，不要输出额外解释。"},
                {"role": "user", "content": prompt},
            ],
            temperature=0,
            timeout=60,
        )
        content = resp.choices[0].message.content or ""
        return _safe_parse_json(content)
    except Exception as e:
        logger.error(f"LLM API 调用失败: {e}")
        return {**_EMPTY_RESULT, "_note": "LLM API 调用失败，请检查配置"}


def _safe_parse_json(content: str) -> dict:
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        match = JSON_PATTERN.search(content)
        if not match:
            logger.warning("LLM 返回无法解析为 JSON")
            return dict(_EMPTY_RESULT)
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            logger.warning("LLM 返回 JSON 片段仍无法解析")
            return dict(_EMPTY_RESULT)
