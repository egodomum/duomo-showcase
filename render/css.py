"""디자인 토큰과 폰트를 CSS로 변환한다. 폰트는 base64로 인라인(외부 의존 0)."""
from __future__ import annotations

import base64
from pathlib import Path
from typing import Any

_FONTS = [
    ("Pretendard", "Pretendard-Regular.woff2"),
    ("PretendardM", "Pretendard-Medium.woff2"),
    ("PretendardSB", "Pretendard-SemiBold.woff2"),
    ("Serif", "NotoSerifDisplay-SemiBold.woff2"),
]


def font_face_block(fonts_dir: Path) -> str:
    """woff2를 base64로 인라인한 @font-face 블록."""
    out = []
    for family, fname in _FONTS:
        p = fonts_dir / fname
        b64 = base64.b64encode(p.read_bytes()).decode()
        out.append(
            f"@font-face{{font-family:'{family}';"
            f"src:url(data:font/woff2;base64,{b64}) format('woff2');"
            f"font-display:block;}}"
        )
    return "".join(out)


def tokens_to_css_vars(tokens: dict[str, Any], accent: str) -> str:
    """:root CSS 변수. accent는 브랜드별로 덮어쓴다."""
    c = tokens["color"]
    layout = tokens.get("layout", {})
    return (
        ":root{"
        f"--bg: {c.get('background', '#FFFFFF')};"
        f"--bg-dark: {c.get('background_alt', '#0A0A0A')};"
        f"--text: {c.get('text_primary', '#1F1F1F')};"
        f"--text-sub: {c.get('secondary', '#888888')};"
        f"--text-inv: {c.get('text_inverse', '#FFFFFF')};"
        f"--accent: {accent};"
        f"--divider: {c.get('divider', '#C4C4C4')};"
        f"--w: {layout.get('max_width', 1000)}px;"
        f"--pad-y: {layout.get('section_inner_padding_y', 160)}px;"
        f"--pad-x: {layout.get('outer_padding_x', 80)}px;"
        "}"
    )


def base_css() -> str:
    """모든 블록 공통 CSS (리셋·중앙정렬·1000px 락)."""
    return (
        "*{margin:0;padding:0;box-sizing:border-box;}"
        "body{width:1000px;background:var(--bg);}"
        ".block{width:1000px;text-align:center;}"
        ".block.dark{background:var(--bg-dark);color:var(--text-inv);}"
        ".block.light{background:var(--bg);color:var(--text);}"
        ".kr{font-family:Pretendard;}"
        ".kr-sb{font-family:PretendardSB;}"
        ".serif{font-family:Serif;font-weight:600;}"
        ".label{font-family:PretendardSB;font-size:14px;letter-spacing:8px;color:var(--accent);}"
        ".divider{width:60px;height:1px;background:var(--accent);margin:0 auto;}"
    )
