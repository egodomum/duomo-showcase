"""소재/특징 — 제목 + 본문 + 매크로 사진."""
from __future__ import annotations

from typing import Any

from blocks.base import BlockSpec, Field, escape_html, nl2br

_CSS = (
    "<style>"
    ".material{padding:var(--pad-y) var(--pad-x);}"
    ".material h4{font-family:PretendardSB;font-size:40px;margin-bottom:32px;}"
    ".material p{font-family:Pretendard;font-size:28px;line-height:1.6;"
    "color:var(--text);margin-bottom:48px;}"
    ".material img{width:1000px;display:block;margin-left:calc(-1*var(--pad-x));}"
    "</style>"
)


class MaterialBlock:
    spec = BlockSpec(
        type="material", label="소재/특징", category="O",
        input_fields=[
            Field("title", "제목", "text"),
            Field("body", "설명(경어체)", "textarea"),
            Field("ref", "매크로 사진", "image"),
        ],
        copy_schema={"title": "string", "body": "string"},
    )

    def render(self, data: dict[str, Any], tokens: dict[str, Any],
               refs: dict[str, str]) -> str:
        macro = refs.get(data.get("ref", ""), "")
        img = f'<img src="{macro}">' if macro else ""
        return (
            _CSS + '<section class="block material light">'
            f'<h4>{escape_html(data.get("title"))}</h4>'
            f'<p>{nl2br(data.get("body"))}</p>{img}</section>'
        )
