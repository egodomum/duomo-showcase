"""hero 블록 렌더 테스트."""
from blocks.hero import HeroBlock


def test_hero_spec():
    b = HeroBlock()
    assert b.spec.type == "hero"
    assert b.spec.category == "U"


def test_hero_renders_serif_product_name_and_korean_sub():
    b = HeroBlock()
    html = b.render(
        data={"product_en": "Camaleonda", "variant": "Fabric",
              "subhead": "은은한 빛이 따뜻한", "ref": "bg"},
        tokens={}, refs={"bg": "data:image/png;base64,AAA"},
    )
    assert "<section" in html and "hero" in html
    assert "Camaleonda" in html
    assert "은은한 빛이 따뜻한" in html
    assert "serif" in html
    assert "data:image/png;base64,AAA" in html


def test_hero_escapes_text():
    b = HeroBlock()
    html = b.render({"product_en": "A&B", "subhead": "<x>", "ref": "bg"},
                    {}, {"bg": "u"})
    assert "A&amp;B" in html
    assert "&lt;x&gt;" in html


def test_hero_no_background_uses_placeholder():
    b = HeroBlock()
    html = b.render({"product_en": "X", "subhead": "y"}, {}, {})
    assert "<section" in html
