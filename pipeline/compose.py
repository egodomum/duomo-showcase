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


def draw_text(
    img: Image.Image,
    *,
    text: str,
    position: tuple[int, int],
    spec: dict[str, Any],
    color: str,
    fonts_dir: Path,
) -> None:
    """text를 position 좌상단 기준으로 img에 그린다.

    자간(letter_spacing_ratio)이 0이 아니면 글자별로 위치 계산해서 그린다.
    """
    font = load_font(spec, fonts_dir)
    draw = ImageDraw.Draw(img)
    spacing_ratio = spec.get("letter_spacing_ratio", 0)

    if abs(spacing_ratio) < 1e-6:
        draw.text(position, text, font=font, fill=color)
        return

    # 자간 적용: 글자별로 위치 계산
    x, y = position
    extra_per_char = int(spec["size_desktop"] * spacing_ratio)
    for ch in text:
        draw.text((x, y), ch, font=font, fill=color)
        bbox = font.getbbox(ch)
        char_width = bbox[2] - bbox[0]
        x += char_width + extra_per_char


def draw_hairline(
    img: Image.Image,
    *,
    position: tuple[int, int],
    length: int,
    color: str,
    thickness: int = 1,
) -> None:
    """골드 헤어라인 가로줄."""
    draw = ImageDraw.Draw(img)
    x, y = position
    for t in range(thickness):
        draw.line([(x, y + t), (x + length, y + t)], fill=color)
