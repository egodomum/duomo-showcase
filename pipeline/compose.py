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


def _background_color(section_cfg: dict, tokens: dict) -> str:
    """섹션 background 모드에서 색상 코드를 결정한다."""
    bg_mode = section_cfg.get("background", "off-white")
    if bg_mode == "off-white":
        return tokens["color"]["background"]
    if bg_mode == "dark":
        return tokens["color"]["background_alt"]
    return tokens["color"]["background"]


def _text_color_for_bg(section_cfg: dict, tokens: dict) -> tuple[str, str]:
    """(primary, secondary) 본문 색상 반환."""
    bg_mode = section_cfg.get("background", "off-white")
    if bg_mode == "dark":
        return tokens["color"]["text_inverse"], tokens["color"]["muted"]
    return tokens["color"]["text_primary"], tokens["color"]["text_secondary"]


def render_typo_section(
    *,
    section_key: str,
    copy_data: dict[str, Any],
    tokens: dict[str, Any],
    fonts_dir: Path,
) -> Image.Image:
    """타이포 중심 섹션을 그린다 (Pain/Problem/Social Proof/Benefits/Risk/Comparison/Target).

    범용 레이아웃:
    - 상단 라벨/헤드라인 영역 (intro/hook/headline)
    - 중앙 본문 영역 (리스트 또는 좌우 컬럼)
    - 하단 마무리 (emotional_hook/reframe/closing)
    """
    section_cfg = tokens["sections"][section_key]
    width = tokens["layout"]["max_width"]
    height = section_cfg["height"]
    bg_color = _background_color(section_cfg, tokens)
    text_primary, text_secondary = _text_color_for_bg(section_cfg, tokens)
    accent = tokens["color"]["accent"]

    img = Image.new("RGB", (width, height), bg_color)

    pad_x = tokens["layout"]["outer_padding_x"]
    pad_y = tokens["layout"]["section_inner_padding_y"]

    # 상단 라벨 또는 헤드라인
    top_text = copy_data.get("intro") or copy_data.get("hook") or copy_data.get("headline")
    if top_text:
        draw_text(
            img,
            text=top_text,
            position=(pad_x, pad_y),
            spec=tokens["typography"]["headline_kr"],
            color=text_primary,
            fonts_dir=fonts_dir,
        )

    # 본문 리스트
    list_items = (
        copy_data.get("pain_points")
        or copy_data.get("reasons")
        or copy_data.get("main_benefits")
        or copy_data.get("recommended")
        or []
    )
    body_y = pad_y + 100
    body_spec = tokens["typography"]["body"]
    line_height = int(body_spec["size_desktop"] * body_spec["line_height_ratio"]) + 12
    for item in list_items[:6]:
        # 골드 대시 + 본문
        draw_text(
            img,
            text="—",
            position=(pad_x, body_y),
            spec=tokens["typography"]["body"],
            color=accent,
            fonts_dir=fonts_dir,
        )
        draw_text(
            img,
            text=item,
            position=(pad_x + 30, body_y),
            spec=tokens["typography"]["body"],
            color=text_primary,
            fonts_dir=fonts_dir,
        )
        body_y += line_height

    # 하단 골드 헤어라인 + 마무리
    closing = (
        copy_data.get("emotional_hook")
        or copy_data.get("reframe")
        or copy_data.get("closing")
        or copy_data.get("question")
    )
    if closing:
        hairline_y = height - pad_y - 50
        draw_hairline(
            img,
            position=(pad_x, hairline_y),
            length=tokens["layout"]["divider_width"],
            color=accent,
        )
        draw_text(
            img,
            text=closing,
            position=(pad_x, hairline_y + 20),
            spec=tokens["typography"]["subheadline"],
            color=text_secondary,
            fonts_dir=fonts_dir,
        )

    return img


def _resize_and_crop(img: Image.Image, target: tuple[int, int]) -> Image.Image:
    """비율 유지하며 target 크기로 center-crop."""
    tw, th = target
    sw, sh = img.size
    target_ratio = tw / th
    src_ratio = sw / sh

    if src_ratio > target_ratio:
        # 원본이 더 넓음 → 높이 기준 리사이즈 후 좌우 자르기
        new_h = th
        new_w = int(sw * (th / sh))
        resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        left = (new_w - tw) // 2
        return resized.crop((left, 0, left + tw, th))
    else:
        new_w = tw
        new_h = int(sh * (tw / sw))
        resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        top = (new_h - th) // 2
        return resized.crop((0, top, tw, top + th))


def _apply_editorial_grade(img: Image.Image) -> Image.Image:
    """채도 -10%, 약간의 워밍 톤."""
    from PIL import ImageEnhance
    img = ImageEnhance.Color(img).enhance(0.9)
    # 워밍 톤: 빨강·노랑 채널 미세 +
    r, g, b = img.split()
    r = r.point(lambda v: min(255, int(v * 1.02)))
    g = g.point(lambda v: min(255, int(v * 1.01)))
    return Image.merge("RGB", (r, g, b))


def _apply_dark_overlay(img: Image.Image, opacity: float = 0.55) -> Image.Image:
    """검정 오버레이를 합성한다."""
    overlay = Image.new("RGBA", img.size, (26, 26, 26, int(255 * opacity)))
    base = img.convert("RGBA")
    out = Image.alpha_composite(base, overlay)
    return out.convert("RGB")


def render_image_section(
    *,
    section_key: str,
    copy_data: dict[str, Any],
    ref_image_path: Path,
    tokens: dict[str, Any],
    fonts_dir: Path,
) -> Image.Image:
    """이미지 기반 섹션 렌더링.

    1. 레퍼런스 이미지 로드 + 리사이즈/크롭
    2. editorial grade 적용
    3. background mode에 따라 dark overlay
    4. 텍스트 오버레이
    """
    section_cfg = tokens["sections"][section_key]
    width = tokens["layout"]["max_width"]
    height = section_cfg["height"]
    accent = tokens["color"]["accent"]

    bg = Image.open(ref_image_path).convert("RGB")
    bg = _resize_and_crop(bg, (width, height))
    bg = _apply_editorial_grade(bg)

    is_dark = section_cfg.get("background") == "image_overlay_dark"
    if is_dark:
        bg = _apply_dark_overlay(bg, opacity=0.55)
        text_primary = tokens["color"]["text_inverse"]
        text_secondary = tokens["color"]["muted"]
    else:
        text_primary = tokens["color"]["text_primary"]
        text_secondary = tokens["color"]["text_secondary"]

    pad_x = tokens["layout"]["outer_padding_x"]
    pad_y = tokens["layout"]["section_inner_padding_y"]

    # 상단 라벨 (urgency_badge 또는 intro)
    badge = copy_data.get("urgency_badge") or copy_data.get("intro")
    if badge:
        draw_hairline(bg, position=(pad_x, pad_y), length=tokens["layout"]["divider_width"],
                      color=accent)
        draw_text(
            bg, text=badge.upper(),
            position=(pad_x, pad_y + 16),
            spec=tokens["typography"]["label_uppercase"],
            color=accent,
            fonts_dir=fonts_dir,
        )

    # 중앙 헤드라인 (headline_options[0] 또는 product_name)
    headline = (
        (copy_data.get("headline_options") or [None])[0]
        or copy_data.get("product_name")
        or copy_data.get("headline")
        or ""
    )
    if headline:
        draw_text(
            bg, text=headline,
            position=(pad_x, height // 2 - 40),
            spec=tokens["typography"]["headline_kr"],
            color=text_primary,
            fonts_dir=fonts_dir,
        )

    # 서브헤드 (subheadline 또는 one_liner)
    sub = copy_data.get("subheadline") or copy_data.get("one_liner")
    if sub:
        draw_text(
            bg, text=sub,
            position=(pad_x, height // 2 + 30),
            spec=tokens["typography"]["subheadline"],
            color=text_secondary,
            fonts_dir=fonts_dir,
        )

    # 하단 CTA (있을 경우)
    cta = copy_data.get("cta_text") or copy_data.get("cta_button")
    if cta:
        draw_text(
            bg, text=cta.upper(),
            position=(pad_x, height - pad_y - 30),
            spec=tokens["typography"]["cta"],
            color=text_primary,
            fonts_dir=fonts_dir,
        )

    return bg
