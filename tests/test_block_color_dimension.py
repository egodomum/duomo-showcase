"""color_options / dimension 블록 테스트."""
from blocks.color_options import ColorOptionsBlock
from blocks.dimension import DimensionBlock
from blocks.registry import get_block


def test_color_options_renders_swatch_grid():
    html = ColorOptionsBlock().render(
        {"label": "패브릭",
         "swatches": [{"name": "Enia 103", "hex": "#8B7E6E"},
                      {"name": "Enia 111", "hex": "#3D4A3A"}]},
        {}, {})
    assert "패브릭" in html
    assert "Enia 103" in html
    assert "#8B7E6E" in html
    assert "swatch" in html


def test_color_options_empty_swatches_ok():
    html = ColorOptionsBlock().render({"label": "색상", "swatches": []}, {}, {})
    assert "<section" in html


def test_dimension_renders_values_and_drawing():
    html = DimensionBlock().render(
        {"values": "W288×D96×H67×SH55", "ref": "d"}, {}, {"d": "data:img"})
    assert "W288" in html
    assert "data:img" in html
    assert "DIMENSION" in html


def test_color_and_dimension_in_registry():
    assert get_block("color_options").spec.type == "color_options"
    assert get_block("dimension").spec.type == "dimension"
