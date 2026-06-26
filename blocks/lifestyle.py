"""라이프스타일 — 풀블리드 인테리어 사진 + (선택) 캡션."""
from __future__ import annotations

from typing import Any

from blocks.base import BlockSpec, Field, escape_html

_CSS = ("<style>.lifestyle img{width:1000px;display:block;}"
        ".lifestyle .cap{padding:40px var(--pad-x);font-family:Pretendard;"
        "font-size:24px;color:var(--text-sub);}"
        ".lifestyle .ph{width:1000px;height:700px;background:#cfcabf;}"
        "</style>")


class LifestyleBlock:
    spec = BlockSpec(
        type="lifestyle", label="라이프스타일 사진", category="U",
        input_fields=[
            Field("ref", "사진", "image"),
            Field("caption", "캡션(선택)", "text"),
        ],
        copy_schema={"caption": "string"},
    )

    def render(self, data: dict[str, Any], tokens: dict[str, Any],
               refs: dict[str, str]) -> str:
        img_src = refs.get(data.get("ref", ""), "")
        img = (f'<img src="{img_src}">' if img_src
               else '<div class="ph"></div>')
        cap = data.get("caption")
        cap_html = f'<div class="cap">{escape_html(cap)}</div>' if cap else ""
        return (_CSS + '<section class="block lifestyle light">'
                f'{img}{cap_html}</section>')
