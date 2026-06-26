"""레시피 → 완성 HTML 빌더 테스트."""
from pathlib import Path

from render.page_builder import build_page

FONTS = Path(__file__).parent.parent / "fonts"


def _recipe():
    return {
        "meta": {"brand": "B&B Italia", "accent": "#1F1F1F"},
        "blocks": [
            {"type": "brand", "data": {"brand": "B&B Italia",
                                       "statement": "1966년", "dark": True}},
            {"type": "intro", "data": {"body": "소개 문단"}},
            {"type": "closing", "data": {"text": "채널톡 문의"}},
        ],
    }


def test_build_page_returns_full_html():
    html = build_page(_recipe(), fonts_dir=FONTS)
    assert html.lstrip().startswith("<!doctype html")
    assert "@font-face" in html
    assert "--accent: #1F1F1F" in html


def test_build_page_preserves_block_order():
    html = build_page(_recipe(), fonts_dir=FONTS)
    i_brand = html.index("1966년")
    i_intro = html.index("소개 문단")
    i_closing = html.index("채널톡 문의")
    assert i_brand < i_intro < i_closing


def test_build_page_skips_unknown_block_gracefully():
    recipe = {"meta": {"brand": "X", "accent": "#1F1F1F"},
              "blocks": [{"type": "nonexistent", "data": {}},
                         {"type": "intro", "data": {"body": "ok"}}]}
    html = build_page(recipe, fonts_dir=FONTS)
    assert "ok" in html


def test_build_page_defaults_accent_from_brand_when_missing():
    recipe = {"meta": {"brand": "Artemide"},
              "blocks": [{"type": "intro", "data": {"body": "x"}}]}
    html = build_page(recipe, fonts_dir=FONTS)
    assert "--accent: #DE0515" in html
