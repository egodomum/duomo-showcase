"""Playwright 렌더러 통합 테스트 (실제 Chromium 사용)."""
from pathlib import Path

from PIL import Image

from render.page_builder import build_page
from render.renderer import render_html_to_png

FONTS = Path(__file__).parent.parent / "fonts"


def test_render_produces_1000px_png(tmp_path):
    recipe = {
        "meta": {"brand": "B&B Italia", "accent": "#1F1F1F"},
        "blocks": [
            {"type": "brand", "data": {"brand": "B&B Italia",
                                       "statement": "1966년 브리아자", "dark": True}},
            {"type": "intro", "data": {"body": "둥근 형태의 소파입니다"}},
        ],
    }
    html = build_page(recipe, fonts_dir=FONTS)
    out = tmp_path / "page.png"
    render_html_to_png(html, out)
    assert out.exists()
    img = Image.open(out)
    assert img.width == 1000
    assert img.height > 300
