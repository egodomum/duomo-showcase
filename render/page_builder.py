"""레시피(블록 리스트) → 완성 1000px HTML 문서."""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from blocks.registry import BlockNotFound, get_block
from render.accents import resolve_accent
from render.css import base_css, font_face_block, tokens_to_css_vars

log = logging.getLogger(__name__)

_TOKENS_PATH = Path(__file__).parent.parent / "design_tokens" / "duomo-detail.json"


def _load_tokens() -> dict[str, Any]:
    return json.loads(_TOKENS_PATH.read_text(encoding="utf-8"))


def build_page(recipe: dict[str, Any], fonts_dir: Path,
               refs: dict[str, str] | None = None) -> str:
    """레시피를 완성 HTML로 빌드한다.

    accent 우선순위: meta.accent > 브랜드 액센트 맵 > _default.
    알 수 없는 블록 타입은 로그 경고 후 건너뛴다.
    """
    refs = refs or {}
    meta = recipe.get("meta", {})
    accent = meta.get("accent") or resolve_accent(meta.get("brand", ""))
    tokens = _load_tokens()

    head = (
        "<!doctype html><html><head><meta charset='utf-8'><style>"
        + font_face_block(fonts_dir)
        + tokens_to_css_vars(tokens, accent)
        + base_css()
        + "</style></head><body>"
    )

    body_parts: list[str] = []
    for entry in recipe.get("blocks", []):
        btype = entry.get("type", "")
        try:
            block = get_block(btype)
        except BlockNotFound:
            log.warning("skipping unknown block: %s", btype)
            continue
        body_parts.append(block.render(entry.get("data", {}), tokens, refs))

    return head + "".join(body_parts) + "</body></html>"
