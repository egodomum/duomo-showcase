"""공식 수입사 신뢰 블록 — 수입사 명 + 혜택 셀 그리드 (무료배송·교환·A/S·KC 등)."""
from __future__ import annotations

from typing import Any

from blocks.base import BlockSpec, Field, escape_html

_CSS = (
    "<style>"
    ".trust{padding:var(--pad-y) var(--pad-x);}"
    ".trust .imp{font-family:Serif;font-size:36px;margin-bottom:48px;}"
    ".trust .cells{display:flex;flex-wrap:wrap;justify-content:center;gap:24px;}"
    ".trust .cell{min-width:260px;padding:28px 0;border:1px solid var(--divider);"
    "font-family:PretendardM;font-size:26px;color:var(--text);}"
    "</style>"
)


class TrustBlock:
    spec = BlockSpec(
        type="trust_block", label="공식 수입사 신뢰블록", category="O",
        input_fields=[
            Field("importer", "수입사 명", "text"),
            Field("benefits", "혜택 리스트", "list"),
        ],
        copy_schema={},
    )

    def render(self, data: dict[str, Any], tokens: dict[str, Any],
               refs: dict[str, str]) -> str:
        cells = "".join(
            f'<div class="cell">{escape_html(b)}</div>'
            for b in data.get("benefits", [])
        )
        return (
            _CSS + '<section class="block trust light">'
            f'<div class="imp">{escape_html(data.get("importer"))}</div>'
            f'<div class="cells">{cells}</div></section>'
        )
