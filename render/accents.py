"""브랜드 액센트 컬러 해석. 골드는 절대 사용하지 않는다(Figma 전수조사 결론)."""
from __future__ import annotations

import json
from pathlib import Path

GOLD = "#D4AF37"
_PATH = Path(__file__).parent.parent / "design_tokens" / "brand_accents.json"
_MAP: dict[str, str] | None = None


def _load() -> dict[str, str]:
    global _MAP
    if _MAP is None:
        _MAP = json.loads(_PATH.read_text(encoding="utf-8"))
    return _MAP


def resolve_accent(brand: str) -> str:
    """브랜드명으로 액센트 hex를 반환한다. 미등록 브랜드는 _default."""
    m = _load()
    lower = {k.lower(): v for k, v in m.items()}
    return lower.get((brand or "").strip().lower(), m["_default"])
