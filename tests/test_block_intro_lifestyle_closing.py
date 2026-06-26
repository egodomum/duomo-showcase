"""intro / lifestyle / closing 블록 테스트."""
from blocks.intro import IntroBlock
from blocks.lifestyle import LifestyleBlock
from blocks.closing import ClosingBlock


def test_intro_centered_body():
    html = IntroBlock().render({"body": "둥근 형태의 소파입니다"}, {}, {})
    assert "둥근 형태의 소파입니다" in html
    assert "intro" in html


def test_lifestyle_fullbleed_image():
    html = LifestyleBlock().render({"caption": "거실", "ref": "img"}, {},
                                   {"img": "data:bg"})
    assert "data:bg" in html
    assert "거실" in html


def test_lifestyle_caption_optional():
    html = LifestyleBlock().render({"ref": "img"}, {}, {"img": "data:bg"})
    assert "<section" in html


def test_closing_soft_cta_no_hardsell():
    html = ClosingBlock().render({"text": "추가 옵션은 채널톡으로 문의해주세요"}, {}, {})
    assert "채널톡" in html
    assert "closing" in html
