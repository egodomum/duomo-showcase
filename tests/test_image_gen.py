"""pipeline.image_gen tests — API 호출 없이 프롬프트 빌더와 에러 처리만 검증."""
import pytest

from pipeline.image_gen import build_background_prompt, generate_background, ImageGenError


BRIEF = {"brand": "B&B Italia", "model": "Charles", "designer": "Antonio Citterio"}


def test_prompt_includes_brand_and_designer():
    cfg = {"mode": "image", "background": "off-white"}
    prompt = build_background_prompt(BRIEF, "05_solution", cfg)
    assert "B&B Italia Charles" in prompt
    assert "Antonio Citterio" in prompt


def test_prompt_forbids_text():
    """텍스트 없는 배경이 핵심 — 프롬프트가 글자 금지를 명시해야 함."""
    cfg = {"mode": "image", "background": "off-white"}
    prompt = build_background_prompt(BRIEF, "01_hero", cfg)
    assert "NO TEXT" in prompt
    assert "1024x1024" in prompt


def test_prompt_dark_mode_uses_twilight():
    cfg = {"mode": "image", "background": "image_overlay_dark"}
    prompt = build_background_prompt(BRIEF, "01_hero", cfg)
    assert "twilight" in prompt.lower() or "dark text overlay" in prompt.lower()


def test_prompt_handles_missing_fields():
    """브랜드만 있고 모델·디자이너 없어도 깨지지 않아야."""
    cfg = {"mode": "image", "background": "off-white"}
    prompt = build_background_prompt({"brand": "Flos"}, "05_solution", cfg)
    assert "Flos" in prompt
    assert "NO TEXT" in prompt


def test_generate_raises_without_api_key(monkeypatch, tmp_path):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(ImageGenError, match="GEMINI_API_KEY"):
        generate_background("test prompt", tmp_path / "out.png", api_key=None)
