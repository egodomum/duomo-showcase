"""블록 base 인터페이스 테스트."""
from blocks.base import BlockSpec, Field, escape_html


def test_field_construction():
    f = Field(key="statement", label="브랜드 철학", kind="textarea")
    assert f.key == "statement"
    assert f.kind == "textarea"


def test_blockspec_construction():
    spec = BlockSpec(
        type="brand", label="브랜드 스테이트먼트", category="U",
        input_fields=[Field("statement", "철학", "textarea")],
        copy_schema={"statement": "string"},
    )
    assert spec.type == "brand"
    assert spec.category == "U"
    assert spec.input_fields[0].key == "statement"


def test_escape_html_blocks_injection():
    assert escape_html("<script>") == "&lt;script&gt;"
    assert escape_html("B&B") == "B&amp;B"
    assert escape_html('a"b') == "a&quot;b"


def test_escape_html_handles_none():
    assert escape_html(None) == ""
