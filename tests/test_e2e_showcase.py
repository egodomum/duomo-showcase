"""전체 파이프라인 E2E: 레시피 → HTML → PNG (실제 Chromium)."""
from pathlib import Path

from PIL import Image

from render.page_builder import build_page
from render.renderer import render_html_to_png

FONTS = Path(__file__).parent.parent / "fonts"


def test_full_showcase_recipe_renders(tmp_path):
    """B&B Camaleonda 풀 레시피가 1000px 세로 PNG로 렌더된다."""
    recipe = {
        "meta": {"brand": "B&B Italia", "product": "Camaleonda",
                 "designer": "Mario Bellini", "category": "furniture",
                 "accent": "#1F1F1F"},
        "blocks": [
            {"type": "brand", "data": {"brand": "B&B Italia",
             "statement": "1966년 브리아자에서 시작되었습니다", "dark": True}},
            {"type": "designer", "data": {"name": "Mario Bellini",
             "bio": "MoMA 영구 소장 디자이너입니다", "dark": True}},
            {"type": "hero", "data": {"product_en": "Camaleonda",
             "variant": "Fabric", "subhead": "모듈로 완성하는 공간"}},
            {"type": "intro", "data": {"body": "둥근 모듈로 자유롭게 구성합니다"}},
            {"type": "color_options", "data": {"label": "패브릭",
             "swatches": [{"name": "Enia 103", "hex": "#8B7E6E"},
                          {"name": "Enia 111", "hex": "#3D4A3A"}]}},
            {"type": "dimension", "data": {"values": "W288×D96×H67×SH55"}},
            {"type": "closing", "data": {"text": "추가 구성은 채널톡으로 문의해주세요"}},
        ],
    }
    html = build_page(recipe, fonts_dir=FONTS)
    out = tmp_path / "camaleonda.png"
    render_html_to_png(html, out)

    img = Image.open(out)
    assert img.width == 1000
    assert img.height > 2000
    px_top = img.getpixel((500, 50))
    assert sum(px_top[:3]) < 200  # 상단 brand 다크
