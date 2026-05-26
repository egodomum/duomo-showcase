"""PIL 기반 13섹션 합성 (이미지 그룹 + 타이포 그룹)."""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

log = logging.getLogger(__name__)


class FontError(Exception):
    """폰트 로딩 실패."""


class ComposeError(Exception):
    """합성 실패."""


def load_tokens(path: Path) -> dict[str, Any]:
    """디자인 토큰 JSON을 로드."""
    return json.loads(path.read_text(encoding="utf-8"))


def load_font(spec: dict[str, Any], fonts_dir: Path) -> ImageFont.FreeTypeFont:
    """타이포 스펙에서 PIL 폰트를 만든다.

    spec 예시: {"font_file": "Pretendard-Light.otf", "size_desktop": 17, ...}
    """
    font_path = fonts_dir / spec["font_file"]
    if not font_path.exists():
        raise FontError(f"Font not found: {font_path}")
    try:
        return ImageFont.truetype(str(font_path), size=spec["size_desktop"])
    except OSError as e:
        raise FontError(f"Failed to load {font_path}: {e}") from e
