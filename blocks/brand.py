"""Brand statement 블록 — 라벨(브랜드명, accent색) + 경어체 철학 문장. 다크/라이트."""
from __future__ import annotations

from typing import Any

from blocks.base import BlockSpec, Field, escape_html, nl2br

_CSS = (
    "<style>"
    ".brand{padding:var(--pad-y) var(--pad-x);}"
    ".brand .label{margin-bottom:44px;text-transform:uppercase;}"
    ".brand p{font-size:40px;line-height:1.44;letter-spacing:-.8px;}"
    "</style>"
)


class BrandBlock:
    spec = BlockSpec(
        type="brand", label="브랜드 스테이트먼트", category="U",
        input_fields=[
            Field("brand", "브랜드명", "text"),
            Field("statement", "브랜드 철학(경어체)", "textarea"),
            Field("dark", "다크 배경", "text"),
        ],
        copy_schema={"statement": "string"},
    )

    def render(self, data: dict[str, Any], tokens: dict[str, Any],
               refs: dict[str, str]) -> str:
        mode = "dark" if data.get("dark") else "light"
        return (
            _CSS +
            f'<section class="block brand {mode}">'
            f'<div class="label">{escape_html(data.get("brand"))}</div>'
            f'<p class="kr-sb">{nl2br(data.get("statement"))}</p>'
            '</section>'
        )
