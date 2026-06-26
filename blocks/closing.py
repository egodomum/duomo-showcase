"""마무리 문의 — 소프트 CTA(채널톡 안내). 하드셀/가격/긴급성 금지."""
from __future__ import annotations

from typing import Any

from blocks.base import BlockSpec, Field, nl2br

_CSS = ("<style>.closing{padding:var(--pad-y) var(--pad-x);}"
        ".closing p{font-size:32px;line-height:1.5;color:var(--text-inv);}"
        "</style>")


class ClosingBlock:
    spec = BlockSpec(
        type="closing", label="마무리 문의", category="U",
        input_fields=[Field("text", "문의 안내(소프트)", "textarea")],
        copy_schema={"text": "string"},
    )

    def render(self, data: dict[str, Any], tokens: dict[str, Any],
               refs: dict[str, str]) -> str:
        return (_CSS + '<section class="block closing dark">'
                f'<p class="kr">{nl2br(data.get("text"))}</p></section>')
