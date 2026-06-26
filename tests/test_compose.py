"""pipeline.compose tests."""
from pathlib import Path

import pytest
from PIL import Image, ImageFont

from pipeline.compose import load_tokens, load_font, FontError


PROJECT_ROOT = Path(__file__).parent.parent
TOKENS_PATH = PROJECT_ROOT / "design_tokens" / "premium-editorial.json"
FONTS_DIR = PROJECT_ROOT / "fonts"
SAMPLE_REF = PROJECT_ROOT / "tests" / "_fixtures" / "sample_ref.jpg"


@pytest.fixture(scope="module", autouse=True)
def _make_sample_ref():
    """테스트용 샘플 배경 이미지 생성."""
    if not SAMPLE_REF.exists():
        SAMPLE_REF.parent.mkdir(parents=True, exist_ok=True)
        # 1600x1000 베이지 그라데이션
        ref = Image.new("RGB", (1600, 1000), "#D9CFC0")
        for y in range(1000):
            r = int(217 - (y / 1000) * 40)
            g = int(207 - (y / 1000) * 35)
            b = int(192 - (y / 1000) * 30)
            for x in range(1600):
                ref.putpixel((x, y), (r, g, b))
        ref.save(SAMPLE_REF, "JPEG", quality=85)
    yield


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


from pipeline.compose import render_image_section, ComposeError


SAMPLE_COPY_HERO = {
    "headline_options": [
        "30년이 지나도 사랑받는 소파, B&B Italia Charles",
        "Antonio Citterio가 1997년 그린 미니멀리즘의 정의",
        "이탈리아 공장에서 1주일에 단 8세트만 만들어지는 모듈러",
    ],
    "subheadline": "DUOMO가 정식 수입하는 정통 이탈리아 가구",
    "urgency_badge": "2026 봄 시즌 한정",
    "cta_text": "전시장 방문 예약",
}


def test_render_image_section_hero():
    tokens = load_tokens(TOKENS_PATH)
    img = render_image_section(
        section_key="01_hero",
        copy_data=SAMPLE_COPY_HERO,
        ref_image_path=SAMPLE_REF,
        tokens=tokens,
        fonts_dir=FONTS_DIR,
    )
    assert img.size == (1200, 800)
    # Hero는 dark overlay 적용되므로 평균 어둠
    pixels = [img.getpixel((x, y)) for x in (100, 600, 1100) for y in (100, 400, 700)]
    avg_brightness = sum(sum(p) for p in pixels) / (len(pixels) * 3)
    assert avg_brightness < 150  # overlay 적용 후 어두워야 함


def test_render_image_section_solution_no_overlay():
    """05_solution은 off-white 배경, dark overlay 없음."""
    tokens = load_tokens(TOKENS_PATH)
    copy = {
        "intro": "DUOMO PRESENTS",
        "product_name": "B&B Italia Charles",
        "one_liner": "미니멀리즘의 정의",
        "target_fit": "20평 이상 거실",
    }
    img = render_image_section(
        section_key="05_solution",
        copy_data=copy,
        ref_image_path=SAMPLE_REF,
        tokens=tokens,
        fonts_dir=FONTS_DIR,
    )
    assert img.size == (1200, 400)


from pipeline.compose import render_section


def test_render_section_dispatches_image_mode():
    tokens = load_tokens(TOKENS_PATH)
    img = render_section(
        section_key="01_hero",
        copy_data=SAMPLE_COPY_HERO,
        tokens=tokens,
        fonts_dir=FONTS_DIR,
        ref_images=[SAMPLE_REF],
    )
    assert img.size == (1200, 800)


def test_render_section_dispatches_typo_mode():
    tokens = load_tokens(TOKENS_PATH)
    img = render_section(
        section_key="02_pain",
        copy_data=SAMPLE_COPY_PAIN,
        tokens=tokens,
        fonts_dir=FONTS_DIR,
        ref_images=[],
    )
    assert img.size == (1200, 600)


def test_render_section_image_mode_requires_ref():
    tokens = load_tokens(TOKENS_PATH)
    with pytest.raises(ComposeError):
        render_section(
            section_key="01_hero",
            copy_data=SAMPLE_COPY_HERO,
            tokens=tokens,
            fonts_dir=FONTS_DIR,
            ref_images=[],
        )
