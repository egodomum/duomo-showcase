"""레시피(블록 리스트) 조작 헬퍼 — UI 세션 상태에서 사용."""
from __future__ import annotations

from typing import Any


def new_recipe(*, brand: str = "", product: str = "", designer: str = "",
               category: str = "furniture", accent: str = "") -> dict[str, Any]:
    """빈 레시피를 만든다."""
    return {
        "meta": {"brand": brand, "product": product, "designer": designer,
                 "category": category, "accent": accent},
        "blocks": [],
    }


def add_block(recipe: dict[str, Any], block_type: str) -> None:
    """블록을 맨 끝에 추가한다."""
    recipe["blocks"].append({"type": block_type, "data": {}})


def remove_block(recipe: dict[str, Any], index: int) -> None:
    """index 블록을 제거한다."""
    if 0 <= index < len(recipe["blocks"]):
        recipe["blocks"].pop(index)


def move_block(recipe: dict[str, Any], index: int, delta: int) -> None:
    """블록을 delta만큼 이동한다(-1 위 / +1 아래). 범위 밖이면 무시."""
    blocks = recipe["blocks"]
    new_idx = index + delta
    if 0 <= index < len(blocks) and 0 <= new_idx < len(blocks):
        blocks[index], blocks[new_idx] = blocks[new_idx], blocks[index]
