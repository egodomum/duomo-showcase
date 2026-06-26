"""Designer 블록 — 'DESIGNER' 라벨 + 이름 + 바이오 + 인물 사진. 보통 다크 배경."""
from __future__ import annotations

from typing import Any

from blocks.base import BlockSpec, Field, escape_html, nl2br

_CSS = (
    "<style>"
    ".designer{padding:var(--pad-y) var(--pad-x);}"
    ".designer .portrait{width:360px;height:440px;object-fit:cover;"
    "margin:0 auto 48px;display:block;}"
    ".designer .role{font-family:PretendardSB;font-size:14px;letter-spacing:8px;"
    "color:var(--accent);margin-bottom:20px;}"
    ".designer h3{font-family:Serif;font-size:48px;margin-bottom:28px;}"
    ".designer p{font-size:24px;line-height:1.6;}"
    "</style>"
)


class DesignerBlock:
    spec = BlockSpec(
        type="designer", label="디자이너", category="U",
        input_fields=[
            Field("name", "디자이너명", "text"),
            Field("bio", "바이오(경어체)", "textarea"),
            Field("ref", "인물 사진", "image"),
            Field("dark", "다크 배경", "text"),
        ],
        copy_schema={"bio": "string"},
    )

    def render(self, data: dict[str, Any], tokens: dict[str, Any],
               refs: dict[str, str]) -> str:
        mode = "dark" if data.get("dark", True) else "light"
        portrait = refs.get(data.get("ref", ""), "")
        img = f'<img class="portrait" src="{portrait}">' if portrait else ""
        return (
            _CSS +
            f'<section class="block designer {mode}">'
            f'{img}'
            '<div class="role">DESIGNER</div>'
            f'<h3>{escape_html(data.get("name"))}</h3>'
            f'<p class="kr">{nl2br(data.get("bio"))}</p>'
            '</section>'
        )
