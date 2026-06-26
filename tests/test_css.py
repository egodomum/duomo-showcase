"""토큰→CSS 변수 + @font-face 빌더 테스트."""
import json
from pathlib import Path

from render.css import tokens_to_css_vars, font_face_block, base_css

PROJECT = Path(__file__).parent.parent
FONTS = PROJECT / "fonts"


def _tokens():
    p = PROJECT / "design_tokens" / "duomo-detail.json"
    return json.loads(p.read_text(encoding="utf-8"))


def test_css_vars_include_accent_override():
    css = tokens_to_css_vars(_tokens(), accent="#29406C")
    assert "--accent: #29406C" in css
    assert "--w: 1000px" in css


def test_css_vars_use_white_background():
    css = tokens_to_css_vars(_tokens(), accent="#1F1F1F")
    assert "--bg: #FFFFFF" in css


def test_font_face_embeds_woff2_base64():
    block = font_face_block(FONTS)
    assert "@font-face" in block
    assert "Pretendard" in block
    assert "Serif" in block
    assert "base64," in block


def test_base_css_centers_and_locks_width():
    css = base_css()
    assert "text-align:center" in css.replace(" ", "")
    assert "1000px" in css
