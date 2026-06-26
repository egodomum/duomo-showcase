"""색상/마감 옵션 — 라벨 + 원형 스와치 그리드 (가구=패브릭/조명=마감)."""
from __future__ import annotations

from typing import Any

from blocks.base import BlockSpec, Field, escape_html

_CSS = (
    "<style>"
    ".coloropt{padding:var(--pad-y) var(--pad-x);}"
    ".coloropt h4{font-family:PretendardSB;font-size:40px;margin-bottom:48px;}"
    ".coloropt .grid{display:flex;flex-wrap:wrap;justify-content:center;gap:32px;}"
    ".coloropt .swatch{width:160px;}"
    ".coloropt .dot{width:80px;height:80px;border-radius:50%;"
    "border:1px solid var(--divider);margin:0 auto 16px;}"
    ".coloropt .nm{font-family:PretendardM;font-size:24px;color:var(--text);}"
    "</style>"
)


class ColorOptionsBlock:
    spec = BlockSpec(
        type="color_options", label="색상/마감 옵션", category="U",
        input_fields=[
            Field("label", "라벨(예: 색상/패브릭)", "text"),
            Field("swatches", "스와치 [{name,hex}]", "list"),
        ],
        copy_schema={"label": "string"},
    )

    def render(self, data: dict[str, Any], tokens: dict[str, Any],
               refs: dict[str, str]) -> str:
        cells = []
        for sw in data.get("swatches", []):
            hexv = escape_html(sw.get("hex", "#CCCCCC"))
            cells.append(
                '<div class="swatch">'
                f'<div class="dot" style="background:{hexv};"></div>'
                f'<div class="nm">{escape_html(sw.get("name"))}</div></div>'
            )
        return (
            _CSS + '<section class="block coloropt light">'
            f'<h4>{escape_html(data.get("label"))}</h4>'
            f'<div class="grid">{"".join(cells)}</div></section>'
        )
