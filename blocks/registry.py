"""블록 타입 → 블록 인스턴스 레지스트리."""
from __future__ import annotations

from blocks.base import Block, BlockSpec
from blocks.brand import BrandBlock
from blocks.closing import ClosingBlock
from blocks.color_options import ColorOptionsBlock
from blocks.designer import DesignerBlock
from blocks.dimension import DimensionBlock
from blocks.hero import HeroBlock
from blocks.intro import IntroBlock
from blocks.lifestyle import LifestyleBlock
from blocks.material import MaterialBlock
from blocks.spec_table import SpecTableBlock
from blocks.trust_block import TrustBlock


class BlockNotFound(Exception):
    """등록되지 않은 블록 타입."""


_REGISTRY: dict[str, Block] = {}


def _register(block: Block) -> None:
    _REGISTRY[block.spec.type] = block


for _b in (HeroBlock(), BrandBlock(), DesignerBlock(),
           IntroBlock(), LifestyleBlock(), ClosingBlock(),
           ColorOptionsBlock(), DimensionBlock(),
           TrustBlock(), SpecTableBlock(), MaterialBlock()):
    _register(_b)


def get_block(block_type: str) -> Block:
    """타입으로 블록 인스턴스를 반환한다."""
    if block_type not in _REGISTRY:
        raise BlockNotFound(f"Unknown block type: {block_type}")
    return _REGISTRY[block_type]


def list_blocks() -> list[BlockSpec]:
    """등록된 모든 블록의 spec 리스트."""
    return [b.spec for b in _REGISTRY.values()]
