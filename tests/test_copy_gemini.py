"""Gemini 카피 생성 테스트 (HTTP 모킹)."""
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from pipeline.copy import CopyError
from pipeline.copy_gemini import generate_block_copy_gemini


def _gemini_response(obj):
    """Gemini generateContent 응답 모양."""
    m = MagicMock()
    m.status_code = 200
    m.json.return_value = {
        "candidates": [
            {"content": {"parts": [{"text": json.dumps(obj, ensure_ascii=False)}]}}
        ]
    }
    return m


def test_generate_returns_dict(tmp_path):
    prompt = tmp_path / "showcase-copy.md"
    prompt.write_text("system", encoding="utf-8")
    with patch("pipeline.copy_gemini.requests.post",
               return_value=_gemini_response({"statement": "1966년 시작되었습니다"})):
        out = generate_block_copy_gemini(
            block_type="brand", copy_schema={"statement": "string"},
            meta={"brand": "B&B Italia"}, system_prompt_path=prompt,
            api_key="fake-key")
    assert out["statement"].startswith("1966")


def test_missing_key_raises(monkeypatch, tmp_path):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    prompt = tmp_path / "p.md"
    prompt.write_text("s", encoding="utf-8")
    with pytest.raises(CopyError, match="GEMINI_API_KEY"):
        generate_block_copy_gemini(
            block_type="brand", copy_schema={}, meta={},
            system_prompt_path=prompt, api_key=None)


def test_api_error_raises(tmp_path):
    prompt = tmp_path / "p.md"
    prompt.write_text("s", encoding="utf-8")
    bad = MagicMock()
    bad.status_code = 429
    bad.text = "rate limit"
    with patch("pipeline.copy_gemini.requests.post", return_value=bad):
        with pytest.raises(CopyError, match="429"):
            generate_block_copy_gemini(
                block_type="brand", copy_schema={}, meta={},
                system_prompt_path=prompt, api_key="fake")
