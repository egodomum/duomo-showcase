"""블록 레지스트리 테스트."""
import pytest

from blocks.registry import get_block, list_blocks, BlockNotFound


def test_core_blocks_registered():
    types = {b.type for b in list_blocks()}
    assert {"hero", "brand", "designer", "intro", "lifestyle", "closing"} <= types


def test_get_block_returns_instance():
    b = get_block("hero")
    assert b.spec.type == "hero"
    assert hasattr(b, "render")


def test_unknown_block_raises():
    with pytest.raises(BlockNotFound):
        get_block("nonexistent")


def test_list_blocks_have_categories():
    for b in list_blocks():
        assert b.category in ("U", "O", "F", "L")
