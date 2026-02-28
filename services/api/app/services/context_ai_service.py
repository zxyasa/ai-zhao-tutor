from __future__ import annotations

import json
from dataclasses import dataclass
from urllib import error as urlerror
from urllib import request as urlrequest

from fastapi import HTTPException, status

from ..config import settings


@dataclass
class ContextAnalysis:
    engine_hint: str | None
    ai_insight: str


def analyze_parent_context(*, tags: list[str], free_text: str) -> ContextAnalysis:
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OPENAI_API_KEY is not configured",
        )

    payload = _call_claude_api(tags=tags, free_text=free_text)
    parsed = _parse_response(payload)
    if parsed:
        return parsed
    return _heuristic_fallback(tags=tags, free_text=free_text)


def _call_claude_api(*, tags: list[str], free_text: str) -> str:
    prompt = (
        "You are an education assistant. Return strict JSON only with keys "
        "'engine_hint' (one of: easier, harder, keep, calm) and 'ai_insight' (short Chinese text). "
        f"tags={tags}; free_text={free_text}"
    )
    body = json.dumps(
        {
            "model": "gpt-4o-mini",
            "temperature": 0.2,
            "messages": [
                {"role": "system", "content": "You are a concise K-6 learning coach."},
                {"role": "user", "content": prompt},
            ],
        }
    ).encode("utf-8")

    req = urlrequest.Request(
        "https://api.openai.com/v1/chat/completions",
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {settings.openai_api_key or ''}",
            "content-type": "application/json",
        },
    )

    try:
        with urlrequest.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urlerror.URLError as exc:
        # Network or upstream outage should not block parent context ingestion.
        # Caller will use heuristic fallback.
        return ""

    choices = data.get("choices", [])
    if not choices:
        return ""
    message = choices[0].get("message", {})
    text = str(message.get("content", "")).strip()
    if text.startswith("```"):
        text = text.strip("`")
        text = text.replace("json\n", "", 1).strip()
    return text


def _parse_response(raw: str) -> ContextAnalysis | None:
    text = (raw or "").strip()
    if not text:
        return None
    try:
        obj = json.loads(text)
    except json.JSONDecodeError:
        return None

    insight = str(obj.get("ai_insight", "")).strip()
    if not insight:
        return None
    hint_raw = str(obj.get("engine_hint", "")).strip().lower()
    hint = hint_raw if hint_raw in {"easier", "harder", "keep", "calm"} else None
    return ContextAnalysis(engine_hint=hint, ai_insight=insight)


def _heuristic_fallback(*, tags: list[str], free_text: str) -> ContextAnalysis:
    bag = " ".join(tags).lower() + " " + free_text.lower()
    hint = "keep"
    if any(token in bag for token in ["tired", "frustrated", "upset", "焦虑", "累"]):
        hint = "easier"
    elif any(token in bag for token in ["confident", "bored", "easy", "轻松", "无聊"]):
        hint = "harder"

    insight = "建议今天先保持稳定节奏，关注孩子情绪与专注状态。"
    if hint == "easier":
        insight = "建议先降低难度并缩短单题时长，优先建立成功体验。"
    elif hint == "harder":
        insight = "可适度提升挑战，加入1-2道进阶题观察稳定性。"
    return ContextAnalysis(engine_hint=hint, ai_insight=insight)
