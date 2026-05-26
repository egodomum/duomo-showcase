"""Claude API로 13섹션 카피 JSON 생성."""
from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)


class CopyError(Exception):
    """카피 생성 실패."""


def _extract_json(text: str) -> dict[str, Any]:
    """응답 텍스트에서 JSON 추출.

    1) 그대로 파싱 시도
    2) 첫 '{' 부터 마지막 '}' 까지 슬라이스 후 파싱
    """
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return json.loads(match.group(0))

    raise json.JSONDecodeError("No JSON found in response", text, 0)


def generate_copy(
    *,
    client,
    brief: dict[str, Any],
    research: dict[str, Any],
    system_prompt_path: Path,
    model: str = "claude-sonnet-4-5",
    max_tokens: int = 8000,
) -> dict[str, Any]:
    """13섹션 카피 JSON을 생성한다.

    응답이 JSON으로 파싱되지 않으면 'JSON only' 메시지를 추가해 1회 재요청.
    그래도 실패하면 CopyError.
    """
    system_prompt = system_prompt_path.read_text(encoding="utf-8")

    user_msg = (
        f"브리프:\n{json.dumps(brief, ensure_ascii=False, indent=2)}\n\n"
        f"리서치:\n{json.dumps(research, ensure_ascii=False, indent=2)}\n\n"
        "13섹션 카피 JSON을 생성해주세요. 출력은 JSON만, 다른 설명 없이."
    )

    for attempt in range(2):
        response = client.messages.create(
            model=model,
            system=system_prompt,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": user_msg}],
        )
        text = response.content[0].text
        try:
            return _extract_json(text)
        except json.JSONDecodeError as e:
            log.warning("copy JSON parse failed (attempt %d): %s", attempt + 1, e)
            user_msg = (
                "이전 응답이 JSON으로 파싱되지 않았습니다. "
                "**JSON만** 출력해주세요. 다른 텍스트·코드펜스 일체 금지.\n\n"
                + user_msg
            )

    raise CopyError("Failed to parse copy JSON after 2 attempts")
