"""브랜드 액센트 맵 로더 테스트."""
import json
from pathlib import Path

from render.accents import resolve_accent, GOLD

ACCENTS = Path(__file__).parent.parent / "design_tokens" / "brand_accents.json"


def test_known_brand_returns_its_accent():
    assert resolve_accent("Artemide") == "#DE0515"
    assert resolve_accent("Flos") == "#29406C"


def test_unknown_brand_returns_default():
    assert resolve_accent("Nonexistent Brand") == "#1F1F1F"


def test_resolve_is_case_insensitive():
    assert resolve_accent("artemide") == "#DE0515"


def test_no_gold_anywhere():
    data = json.loads(ACCENTS.read_text(encoding="utf-8"))
    assert GOLD == "#D4AF37"
    assert all(v.upper() != GOLD for v in data.values())
