"""13장의 섹션 PNG를 세로로 이어붙여 최종 합본을 만든다.

기반: ~/.claude/skills/landing-page-generator/scripts/stitch_images.py
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from PIL import Image

FIXED_WIDTH = 1200

SECTION_ORDER = [
    "01_hero", "02_pain", "03_problem", "04_story", "05_solution",
    "06_how_it_works", "07_social_proof", "08_authority", "09_benefits",
    "10_risk_removal", "11_comparison", "12_target_filter", "13_final_cta",
]


def stitch_sections(
    section_images: dict[str, Path],
    output_path: Path,
) -> Path:
    """섹션 PNG들을 SECTION_ORDER 순으로 세로 이어붙인다.

    Args:
        section_images: section_key -> 섹션 PNG 경로
        output_path: 최종 합본 PNG 경로 (.pdf 면 PDF로도 저장)
    """
    pages = []
    for key in SECTION_ORDER:
        if key not in section_images:
            continue
        img = Image.open(section_images[key]).convert("RGB")
        if img.width != FIXED_WIDTH:
            ratio = FIXED_WIDTH / img.width
            new_h = int(img.height * ratio)
            img = img.resize((FIXED_WIDTH, new_h), Image.Resampling.LANCZOS)
        pages.append(img)

    if not pages:
        raise ValueError("No section images provided")

    total_h = sum(p.height for p in pages)
    canvas = Image.new("RGB", (FIXED_WIDTH, total_h), "#FAFAF7")
    y = 0
    for p in pages:
        canvas.paste(p, (0, y))
        y += p.height

    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.suffix.lower() == ".pdf":
        canvas.save(output_path, "PDF", resolution=150)
    else:
        canvas.save(output_path, "PNG", optimize=True)
    return output_path
