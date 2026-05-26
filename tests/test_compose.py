"""pipeline.compose tests."""
from pathlib import Path

import pytest
from PIL import ImageFont

from pipeline.compose import load_tokens, load_font, FontError


PROJECT_ROOT = Path(__file__).parent.parent
TOKENS_PATH = PROJECT_ROOT / "design_tokens" / "premium-editorial.json"
FONTS_DIR = PROJECT_ROOT / "fonts"


def test_load_tokens():
    tokens = load_tokens(TOKENS_PATH)
    assert tokens["preset_name"] == "premium-editorial"
    assert tokens["color"]["accent"] == "#B8975A"
    assert tokens["sections"]["01_hero"]["height"] == 800


def test_load_font_returns_pil_font():
    tokens = load_tokens(TOKENS_PATH)
    font = load_font(tokens["typography"]["body"], fonts_dir=FONTS_DIR)
    assert isinstance(font, ImageFont.FreeTypeFont)


def test_load_font_raises_on_missing_file():
    fake_spec = {"font_file": "DoesNotExist.ttf", "size_desktop": 16,
                 "letter_spacing_ratio": 0, "line_height_ratio": 1.4}
    with pytest.raises(FontError):
        load_font(fake_spec, fonts_dir=FONTS_DIR)


from PIL import Image
from pipeline.compose import draw_text


def test_draw_text_writes_pixels():
    """텍스트를 그리면 그 영역의 픽셀이 색상과 일치해야 한다."""
    tokens = load_tokens(TOKENS_PATH)
    img = Image.new("RGB", (400, 100), "#FFFFFF")
    draw_text(
        img,
        text="안녕",
        position=(20, 20),
        spec=tokens["typography"]["headline_kr"],
        color="#000000",
        fonts_dir=FONTS_DIR,
    )
    # 텍스트가 그려진 영역 어딘가에는 검정 픽셀이 있어야 함
    found_black = False
    for x in range(20, 200):
        for y in range(20, 80):
            r, g, b = img.getpixel((x, y))
            if r < 30 and g < 30 and b < 30:
                found_black = True
                break
        if found_black:
            break
    assert found_black, "draw_text가 픽셀을 그리지 않음"
