"""Gemini 무료 티어로 쇼케이스 블록 카피(JSON)를 생성한다. Anthropic 불필요·카드 불필요.

Gemini 텍스트 모델 + responseMimeType=application/json 으로 유효 JSON을 강제한다.
키 발급: https://aistudio.google.com/apikey (Google 계정만 있으면 됨, 무료 티어)
"""
from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any, Optional

import requests

from pipeline.copy import CopyError, _extract_json

log = logging.getLogger(__name__)

DEFAULT_MODEL = os.getenv("GEMINI_TEXT_MODEL", "gemini-2.5-flash")
API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"
TIMEOUT_S = 60


def generate_block_copy_gemini(
    *,
    block_type: str,
    copy_schema: dict,
    meta: dict,
    system_prompt_path: Path,
    api_key: Optional[str] = None,
    model: str = DEFAULT_MODEL,
) -> dict[str, Any]:
    """쇼케이스 블록 하나의 카피를 Gemini로 생성한다.

    Raises:
        CopyError: 키 없음 / API 오류 / JSON 파싱 2회 실패
    """
    api_key = api_key or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise CopyError(
            "GEMINI_API_KEY가 없습니다. https://aistudio.google.com/apikey 에서 "
            "무료 키를 발급받으세요(카드 불필요)."
        )

    system = system_prompt_path.read_text(encoding="utf-8")
    user = (
        f"블록타입: {block_type}\n"
        f"copy_schema: {json.dumps(copy_schema, ensure_ascii=False)}\n"
        f"meta: {json.dumps(meta, ensure_ascii=False)}\n\n"
        "copy_schema의 키를 모두 채운 JSON만 출력하라."
    )
    url = f"{API_BASE}/{model}:generateContent?key={api_key}"
    payload = {
        "system_instruction": {"parts": [{"text": system}]},
        "contents": [{"parts": [{"text": user}]}],
        "generationConfig": {"responseMimeType": "application/json", "temperature": 0.7},
    }

    last_err: Optional[Exception] = None
    for attempt in range(2):
        try:
            resp = requests.post(url, json=payload, timeout=TIMEOUT_S)
        except requests.RequestException as e:
            raise CopyError(f"Gemini 요청 실패: {e}") from e
        if resp.status_code != 200:
            raise CopyError(f"Gemini API {resp.status_code}: {resp.text[:200]}")
        try:
            text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
            return _extract_json(text)
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            last_err = e
            log.warning("gemini copy parse 실패(attempt %d): %s", attempt + 1, e)

    raise CopyError(f"Gemini 카피 JSON 파싱 2회 실패: {last_err}")
