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
