"""Claude API로 리서치/카피/디자인 방향 JSON 생성."""
from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)


class CopyError(Exception):
    """Claude 응답 파싱 실패."""


def _extract_json(text: str) -> dict[str, Any]:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return json.loads(match.group(0))
    raise json.JSONDecodeError("No JSON found", text, 0)


def _call_with_retry(
    *,
    client,
    system_prompt: str,
    user_msg: str,
    model: str,
    max_tokens: int,
    label: str,
) -> dict[str, Any]:
    current = user_msg
    for attempt in range(2):
        response = client.messages.create(
            model=model,
            system=system_prompt,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": current}],
        )
        text = response.content[0].text
        try:
            return _extract_json(text)
        except json.JSONDecodeError as e:
            log.warning("%s JSON parse failed (attempt %d): %s", label, attempt + 1, e)
            current = (
                "이전 응답이 JSON으로 파싱되지 않았습니다. **JSON만** 출력해주세요. "
                "다른 텍스트·코드펜스 일체 금지.\n\n" + current
            )
    raise CopyError(f"Failed to parse {label} JSON after 2 attempts")


def generate_research(
    *,
    client,
    brief: dict[str, Any],
    system_prompt_path: Path,
    model: str = "claude-sonnet-4-5",
    max_tokens: int = 6000,
) -> dict[str, Any]:
    """02-research.md 시스템 프롬프트로 리서치 JSON 생성."""
    user_msg = (
        f"브리프:\n{json.dumps(brief, ensure_ascii=False, indent=2)}\n\n"
        "리서치 JSON을 생성해주세요. 출력은 JSON만."
    )
    return _call_with_retry(
        client=client,
        system_prompt=system_prompt_path.read_text(encoding="utf-8"),
        user_msg=user_msg,
        model=model,
        max_tokens=max_tokens,
        label="research",
    )


def generate_copy(
    *,
    client,
    brief: dict[str, Any],
    research: dict[str, Any],
    system_prompt_path: Path,
    model: str = "claude-sonnet-4-5",
    max_tokens: int = 8000,
) -> dict[str, Any]:
    """03-copy.md 시스템 프롬프트로 13섹션 카피 JSON 생성."""
    user_msg = (
        f"브리프:\n{json.dumps(brief, ensure_ascii=False, indent=2)}\n\n"
        f"리서치:\n{json.dumps(research, ensure_ascii=False, indent=2)}\n\n"
        "13섹션 카피 JSON을 생성해주세요. 출력은 JSON만."
    )
    return _call_with_retry(
        client=client,
        system_prompt=system_prompt_path.read_text(encoding="utf-8"),
        user_msg=user_msg,
        model=model,
        max_tokens=max_tokens,
        label="copy",
    )


def generate_design_direction(
    *,
    client,
    brief: dict[str, Any],
    research: dict[str, Any],
    system_prompt_path: Path,
    model: str = "claude-sonnet-4-5",
    max_tokens: int = 4000,
) -> dict[str, Any]:
    """04-design-direction.md 시스템 프롬프트로 디자인 방향 JSON 생성."""
    user_msg = (
        f"브리프:\n{json.dumps(brief, ensure_ascii=False, indent=2)}\n\n"
        f"리서치:\n{json.dumps(research, ensure_ascii=False, indent=2)}\n\n"
        "디자인 방향 JSON을 생성해주세요. 출력은 JSON만."
    )
    return _call_with_retry(
        client=client,
        system_prompt=system_prompt_path.read_text(encoding="utf-8"),
        user_msg=user_msg,
        model=model,
        max_tokens=max_tokens,
        label="design",
    )


def generate_block_copy(
    *,
    client,
    block_type: str,
    copy_schema: dict,
    meta: dict,
    system_prompt_path: Path,
    model: str = "claude-sonnet-4-5",
    max_tokens: int = 2000,
) -> dict:
    """쇼케이스 블록 하나의 카피를 생성한다. JSON 파싱 실패 시 1회 재시도.

    Raises:
        CopyError: 2회 시도 후에도 JSON 파싱 실패
    """
    system = system_prompt_path.read_text(encoding="utf-8")
    user = (
        f"블록타입: {block_type}\n"
        f"copy_schema: {json.dumps(copy_schema, ensure_ascii=False)}\n"
        f"meta: {json.dumps(meta, ensure_ascii=False)}\n\n"
        "copy_schema의 키를 모두 채운 JSON만 출력하라."
    )
    return _call_with_retry(
        client=client, system_prompt=system, user_msg=user,
        model=model, max_tokens=max_tokens, label=f"block:{block_type}",
    )
