"""치수 — 'DIMENSION' 라벨 + 값(W×D×H×SH) + (선택) 라인 도면 이미지."""
from __future__ import annotations

from typing import Any

from blocks.base import BlockSpec, Field, escape_html

_CSS = (
    "<style>"
    ".dim{padding:var(--pad-y) var(--pad-x);}"
    ".dim .role{font-family:PretendardSB;font-size:14px;letter-spacing:8px;"
    "color:var(--accent);margin-bottom:32px;}"
    ".dim img{max-width:700px;display:block;margin:0 auto 32px;}"
    ".dim .val{font-family:PretendardM;font-size:28px;color:var(--text);}"
    "</style>"
)


class DimensionBlock:
    spec = BlockSpec(
        type="dimension", label="치수", category="O",
        input_fields=[
            Field("values", "치수값(예: W288×D96×H67×SH55)", "text"),
            Field("ref", "도면 이미지(선택)", "image"),
        ],
        copy_schema={},
    )

    def render(self, data: dict[str, Any], tokens: dict[str, Any],
               refs: dict[str, str]) -> str:
        drawing = refs.get(data.get("ref", ""), "")
        img = f'<img src="{drawing}">' if drawing else ""
        return (
            _CSS + '<section class="block dim light">'
            '<div class="role">DIMENSION</div>'
            f'{img}<div class="val">{escape_html(data.get("values"))}</div>'
            '</section>'
        )
