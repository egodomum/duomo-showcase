"""Hero 블록 — 풀블리드 배경 + 다크 오버레이 + 중앙 하단 텍스트(한글 서브→세리프 제품명)."""
from __future__ import annotations

from typing import Any

from blocks.base import BlockSpec, Field, escape_html

_CSS = (
    "<style>"
    ".hero{position:relative;height:1200px;background-size:cover;background-position:center;}"
    ".hero .ov{position:absolute;inset:0;background:rgba(10,10,10,.55);}"
    ".hero .ht{position:absolute;bottom:140px;left:0;right:0;color:#fff;}"
    ".hero .sub{font-size:40px;letter-spacing:-.8px;margin-bottom:24px;}"
    ".hero h1{font-size:106px;line-height:1;}"
    ".hero h2{font-size:80px;line-height:1;margin-top:12px;}"
    "</style>"
)


class HeroBlock:
    spec = BlockSpec(
        type="hero", label="히어로 (제품명)", category="U",
        input_fields=[
            Field("product_en", "제품명(영문)", "text"),
            Field("variant", "변형명", "text"),
            Field("subhead", "한글 서브카피", "text"),
            Field("ref", "배경 이미지", "image"),
        ],
        copy_schema={"product_en": "string", "variant": "string", "subhead": "string"},
    )

    def render(self, data: dict[str, Any], tokens: dict[str, Any],
               refs: dict[str, str]) -> str:
        bg = refs.get(data.get("ref", ""), "")
        style = f"background-image:url('{bg}');" if bg else "background:#9a9a9a;"
        variant = data.get("variant")
        v_html = f'<h2 class="serif">{escape_html(variant)}</h2>' if variant else ""
        return (
            _CSS +
            f'<section class="block hero" style="{style}">'
            '<div class="ov"></div>'
            '<div class="ht">'
            f'<div class="sub kr">{escape_html(data.get("subhead"))}</div>'
            f'<h1 class="serif">{escape_html(data.get("product_en"))}</h1>'
            f'{v_html}'
            '</div></section>'
        )
