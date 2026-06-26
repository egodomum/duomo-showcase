"""trust_block / spec_table / material 블록 테스트."""
from blocks.trust_block import TrustBlock
from blocks.spec_table import SpecTableBlock
from blocks.material import MaterialBlock
from blocks.registry import get_block


def test_trust_block_renders_importer_and_benefits():
    html = TrustBlock().render(
        {"importer": "DUOMO&Co. 한국 공식 수입사",
         "benefits": ["무료배송", "5년 A/S", "KC인증"]}, {}, {})
    assert "공식 수입사" in html
    assert "무료배송" in html
    assert "KC인증" in html


def test_spec_table_renders_rows():
    html = SpecTableBlock().render(
        {"rows": [["품명", "Camaleonda"], ["소재", "Fabric"],
                  ["KC인증", "ZW11055-22008"]]}, {}, {})
    assert "품명" in html
    assert "Camaleonda" in html
    assert "ZW11055-22008" in html


def test_material_renders_text_and_macro():
    html = MaterialBlock().render(
        {"title": "소재", "body": "투명 크리스탈", "ref": "m"}, {}, {"m": "data:img"})
    assert "투명 크리스탈" in html
    assert "data:img" in html


def test_all_three_in_registry():
    for t in ("trust_block", "spec_table", "material"):
        assert get_block(t).spec.type == t
