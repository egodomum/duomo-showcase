"""brand / designer 블록 테스트."""
from blocks.brand import BrandBlock
from blocks.designer import DesignerBlock


def test_brand_renders_label_and_statement():
    b = BrandBlock()
    html = b.render({"brand": "B&B Italia", "statement": "1966년 브리아자",
                     "dark": False}, {}, {})
    assert "B&amp;B Italia" in html
    assert "1966" in html
    assert "label" in html
    assert "light" in html


def test_brand_dark_mode():
    b = BrandBlock()
    html = b.render({"brand": "Flos", "statement": "s", "dark": True}, {}, {})
    assert "dark" in html


def test_designer_renders_name_bio_portrait():
    d = DesignerBlock()
    html = d.render({"name": "Mario Bellini", "bio": "MoMA 영구 소장",
                     "ref": "p", "dark": True}, {}, {"p": "data:img"})
    assert "Mario Bellini" in html
    assert "MoMA" in html
    assert "DESIGNER" in html
    assert "data:img" in html


def test_designer_without_portrait_ok():
    d = DesignerBlock()
    html = d.render({"name": "X", "bio": "y"}, {}, {})
    assert "<section" in html
