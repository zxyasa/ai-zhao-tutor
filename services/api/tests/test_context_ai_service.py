import pytest
from fastapi import HTTPException

from app.services import context_ai_service


def test_analyze_parent_context_parses_mocked_claude(monkeypatch):
    monkeypatch.setattr(context_ai_service.settings, "openai_api_key", "test-key")
    monkeypatch.setattr(
        context_ai_service,
        "_call_claude_api",
        lambda **_: '{"engine_hint":"easier","ai_insight":"今天先降低难度。"}',
    )

    result = context_ai_service.analyze_parent_context(tags=["tired"], free_text="状态一般")
    assert result.engine_hint == "easier"
    assert "降低难度" in result.ai_insight


def test_missing_key_returns_503(monkeypatch):
    monkeypatch.setattr(context_ai_service.settings, "openai_api_key", None)
    with pytest.raises(HTTPException) as exc:
        context_ai_service.analyze_parent_context(tags=["tired"], free_text="状态一般")
    assert exc.value.status_code == 503
    assert "OPENAI_API_KEY" in str(exc.value.detail)
