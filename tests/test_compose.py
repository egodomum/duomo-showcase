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


from pipeline.compose import render_typo_section


SAMPLE_COPY_PAIN = {
    "intro": "이런 고민, 익숙하지 않으세요?",
    "pain_points": [
        "백화점 가구는 어디나 비슷합니다",
        "병행 수입은 진품 보증이 불안합니다",
        "원하는 모델을 어디서 사야 할지 모릅니다",
    ],
    "emotional_hook": "공간이 평범해지는 이유는, 진짜를 만나지 못해서입니다.",
}


def test_render_typo_section_pain():
    tokens = load_tokens(TOKENS_PATH)
    img = render_typo_section(
        section_key="02_pain",
        copy_data=SAMPLE_COPY_PAIN,
        tokens=tokens,
        fonts_dir=FONTS_DIR,
    )
    assert img.size == (1200, 600)
    # off-white 배경: 모서리 픽셀이 거의 #FAFAF7
    r, g, b = img.getpixel((0, 0))
    assert r > 240 and g > 240 and b > 230


def test_render_typo_section_dark_mode():
    """03_problem은 dark 배경."""
    tokens = load_tokens(TOKENS_PATH)
    copy_data = {
        "hook": "당신 안목이 부족한 게 아닙니다",
        "reasons": ["이유 1", "이유 2", "이유 3"],
        "reframe": "결국 정식 수입 큐레이션이 답입니다.",
    }
    img = render_typo_section(
        section_key="03_problem",
        copy_data=copy_data,
        tokens=tokens,
        fonts_dir=FONTS_DIR,
    )
    r, g, b = img.getpixel((0, 0))
    # 다크 배경: #1A1A1A
    assert r < 50 and g < 50 and b < 50
