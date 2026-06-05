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


def _spacing_px(spec: dict[str, Any]) -> int:
    """타이포 스펙의 자간을 픽셀로 환산."""
    return int(spec["size_desktop"] * spec.get("letter_spacing_ratio", 0))


def _line_width(text: str, font: ImageFont.FreeTypeFont, spacing_px: int) -> float:
    """draw_text와 동일한 방식으로 한 줄의 픽셀 너비를 잰다."""
    if not text:
        return 0.0
    if spacing_px == 0:
        return font.getlength(text)
    width = 0.0
    for ch in text:
        bbox = font.getbbox(ch)
        width += (bbox[2] - bbox[0]) + spacing_px
    return width


def wrap_text(
    text: str,
    font: ImageFont.FreeTypeFont,
    spacing_px: int,
    max_width: int,
) -> list[str]:
    """max_width(px)에 맞춰 텍스트를 여러 줄로 나눈다.

    공백 단위(어절)로 먼저 끊고, 한 어절이 너무 길면 글자 단위로 끊는다.
    한글·영문 혼용 모두 안전하게 처리한다.
    """
    if not text:
        return []
    lines: list[str] = []
    current = ""
    for word in text.split(" "):
        candidate = word if not current else current + " " + word
        if _line_width(candidate, font, spacing_px) <= max_width:
            current = candidate
            continue
        if current:
            lines.append(current)
            current = ""
        # 어절 자체가 max_width를 넘으면 글자 단위로 강제 분할
        if _line_width(word, font, spacing_px) <= max_width:
            current = word
        else:
            chunk = ""
            for ch in word:
                if _line_width(chunk + ch, font, spacing_px) <= max_width:
                    chunk += ch
                else:
                    if chunk:
                        lines.append(chunk)
                    chunk = ch
            current = chunk
    if current:
        lines.append(current)
    return lines


def _line_height(spec: dict[str, Any]) -> int:
    """스펙의 줄 높이(px)."""
    return int(spec["size_desktop"] * spec.get("line_height_ratio", 1.4))


def draw_paragraph(
    img: Image.Image,
    *,
    text: str,
    position: tuple[int, int],
    spec: dict[str, Any],
    color: str,
    fonts_dir: Path,
    max_width: int,
) -> int:
    """줄바꿈을 적용해 문단을 그리고, 마지막 줄 다음의 y 좌표를 반환한다."""
    font = load_font(spec, fonts_dir)
    lines = wrap_text(text, font, _spacing_px(spec), max_width)
    x, y = position
    lh = _line_height(spec)
    for line in lines:
        draw_text(img, text=line, position=(x, y), spec=spec, color=color, fonts_dir=fonts_dir)
        y += lh
    return y


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
    max_width = width - 2 * pad_x

    # 위에서 아래로 흐르는 y 커서 (고정 좌표 충돌 방지)
    y = pad_y

    # 상단 헤드라인
    top_text = copy_data.get("intro") or copy_data.get("hook") or copy_data.get("headline")
    if top_text:
        y = draw_paragraph(
            img,
            text=top_text,
            position=(pad_x, y),
            spec=tokens["typography"]["headline_kr"],
            color=text_primary,
            fonts_dir=fonts_dir,
            max_width=max_width,
        )
        y += 36  # 헤드라인 다음 여백

    # 본문 리스트 (골드 대시 + 줄바꿈되는 본문)
    list_items = (
        copy_data.get("pain_points")
        or copy_data.get("reasons")
        or copy_data.get("main_benefits")
        or copy_data.get("recommended")
        or []
    )
    body_spec = tokens["typography"]["body"]
    dash_offset = 30
    list_max_width = max_width - dash_offset
    for item in list_items[:6]:
        draw_text(
            img,
            text="—",
            position=(pad_x, y),
            spec=body_spec,
            color=accent,
            fonts_dir=fonts_dir,
        )
        end_y = draw_paragraph(
            img,
            text=item,
            position=(pad_x + dash_offset, y),
            spec=body_spec,
            color=text_primary,
            fonts_dir=fonts_dir,
            max_width=list_max_width,
        )
        y = end_y + 14  # 항목 간 여백

    # 하단 골드 헤어라인 + 마무리 (y 커서 이어서 — 겹치지 않음)
    closing = (
        copy_data.get("emotional_hook")
        or copy_data.get("reframe")
        or copy_data.get("closing")
        or copy_data.get("question")
    )
    if closing:
        y += 16
        draw_hairline(
            img,
            position=(pad_x, y),
            length=tokens["layout"]["divider_width"],
            color=accent,
        )
        y += 20
        draw_paragraph(
            img,
            text=closing,
            position=(pad_x, y),
            spec=tokens["typography"]["subheadline"],
            color=text_secondary,
            fonts_dir=fonts_dir,
            max_width=max_width,
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
    max_width = width - 2 * pad_x

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

    # 하단 CTA 위치 선계산 (있을 경우)
    cta = copy_data.get("cta_text") or copy_data.get("cta_button")
    cta_y = height - pad_y - 30

    # 중앙 블록(헤드라인 + 서브) — 줄바꿈 후 블록 높이를 재서 수직 중앙 배치
    headline = (
        (copy_data.get("headline_options") or [None])[0]
        or copy_data.get("product_name")
        or copy_data.get("headline")
        or ""
    )
    sub = copy_data.get("subheadline") or copy_data.get("one_liner")

    hl_spec = tokens["typography"]["headline_kr"]
    sub_spec = tokens["typography"]["subheadline"]
    hl_font = load_font(hl_spec, fonts_dir)
    sub_font = load_font(sub_spec, fonts_dir)
    hl_lines = wrap_text(headline, hl_font, _spacing_px(hl_spec), max_width) if headline else []
    sub_lines = wrap_text(sub, sub_font, _spacing_px(sub_spec), max_width) if sub else []
    hl_lh = _line_height(hl_spec)
    sub_lh = _line_height(sub_spec)
    gap = 24

    block_h = (
        len(hl_lines) * hl_lh
        + (gap if hl_lines and sub_lines else 0)
        + len(sub_lines) * sub_lh
    )

    top_limit = pad_y + 50
    bottom_limit = (cta_y - 24) if cta else (height - pad_y)
    avail = bottom_limit - top_limit
    y = top_limit + max(0, (avail - block_h) // 2)

    for line in hl_lines:
        draw_text(bg, text=line, position=(pad_x, y), spec=hl_spec,
                  color=text_primary, fonts_dir=fonts_dir)
        y += hl_lh
    if hl_lines and sub_lines:
        y += gap
    for line in sub_lines:
        draw_text(bg, text=line, position=(pad_x, y), spec=sub_spec,
                  color=text_secondary, fonts_dir=fonts_dir)
        y += sub_lh

    # 하단 CTA
    if cta:
        draw_text(
            bg, text=cta.upper(),
            position=(pad_x, cta_y),
            spec=tokens["typography"]["cta"],
            color=text_primary,
            fonts_dir=fonts_dir,
        )

    return bg


def render_section(
    *,
    section_key: str,
    copy_data: dict[str, Any],
    tokens: dict[str, Any],
    fonts_dir: Path,
    ref_images: list[Path],
) -> Image.Image:
    """섹션 모드에 따라 image/typo/image_split 렌더러로 분기."""
    section_cfg = tokens["sections"][section_key]
    mode = section_cfg["mode"]

    if mode == "typo":
        return render_typo_section(
            section_key=section_key,
            copy_data=copy_data,
            tokens=tokens,
            fonts_dir=fonts_dir,
        )

    if mode in ("image", "image_split"):
        if not ref_images:
            raise ComposeError(
                f"Section {section_key} requires reference image but none provided"
            )
        # MVP: image_split도 첫 번째 이미지만 사용 (V2에서 좌/우 합성 분리)
        return render_image_section(
            section_key=section_key,
            copy_data=copy_data,
            ref_image_path=ref_images[0],
            tokens=tokens,
            fonts_dir=fonts_dir,
        )

    raise ComposeError(f"Unknown section mode: {mode}")
