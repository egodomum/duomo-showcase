"""상품정보 스펙표 — 라벨/값 2열 행 리스트."""
from __future__ import annotations

from typing import Any

from blocks.base import BlockSpec, Field, escape_html

_CSS = (
    "<style>"
    ".spec{padding:var(--pad-y) var(--pad-x);}"
    ".spec table{width:100%;border-collapse:collapse;font-family:Pretendard;}"
    ".spec td{padding:20px 8px;border-bottom:1px solid var(--divider);font-size:24px;}"
    ".spec td.k{text-align:left;color:var(--text-sub);width:30%;}"
    ".spec td.v{text-align:left;color:var(--text);}"
    "</style>"
)


class SpecTableBlock:
    spec = BlockSpec(
        type="spec_table", label="상품정보 스펙표", category="O",
        input_fields=[Field("rows", "행 [[라벨,값],...]", "list")],
        copy_schema={},
    )

    def render(self, data: dict[str, Any], tokens: dict[str, Any],
               refs: dict[str, str]) -> str:
        rows = "".join(
            f'<tr><td class="k">{escape_html(r[0])}</td>'
            f'<td class="v">{escape_html(r[1])}</td></tr>'
            for r in data.get("rows", []) if len(r) >= 2
        )
        return (_CSS + '<section class="block spec light">'
                f'<table>{rows}</table></section>')
