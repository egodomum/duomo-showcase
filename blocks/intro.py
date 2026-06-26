"""제품 소개 문단 — 흰 배경, 중앙, 경어체 본문."""
from __future__ import annotations

from typing import Any

from blocks.base import BlockSpec, Field, nl2br

_CSS = ("<style>.intro{padding:var(--pad-y) var(--pad-x);}"
        ".intro p{font-size:40px;line-height:1.44;letter-spacing:-.8px;color:var(--text);}"
        "</style>")


class IntroBlock:
    spec = BlockSpec(
        type="intro", label="제품 소개", category="U",
        input_fields=[Field("body", "소개 문단(경어체)", "textarea")],
        copy_schema={"body": "string"},
    )

    def render(self, data: dict[str, Any], tokens: dict[str, Any],
               refs: dict[str, str]) -> str:
        return (_CSS + '<section class="block intro light">'
                f'<p class="kr-sb">{nl2br(data.get("body"))}</p></section>')
