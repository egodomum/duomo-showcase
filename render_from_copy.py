"""카피 JSON을 받아 13섹션 상세페이지를 합성한다.

옵션 A 흐름: Claude(대화 세션)가 카피를 직접 작성 → JSON 저장 → 이 스크립트로 합성.
Anthropic/Gemini API 호출 없음. 비용 0.

사용법:
    python render_from_copy.py <copy.json> [ref_image.jpg] [out_dir]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from pipeline.compose import render_section, load_tokens
from pipeline.stitch import stitch_sections

PROJECT = Path(__file__).parent
TOKENS_PATH = PROJECT / "design_tokens" / "premium-editorial.json"
FONTS_DIR = PROJECT / "fonts"
DEFAULT_REF = PROJECT / "tests" / "_fixtures" / "sample_ref.jpg"


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python render_from_copy.py <copy.json> [ref_image] [out_dir]")
        sys.exit(1)

    copy_path = Path(sys.argv[1])
    ref_image = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_REF
    out_dir = Path(sys.argv[3]) if len(sys.argv) > 3 else copy_path.parent / "render"

    copy = json.loads(copy_path.read_text(encoding="utf-8"))
    tokens = load_tokens(TOKENS_PATH)
    out_dir.mkdir(parents=True, exist_ok=True)

    section_paths: dict[str, Path] = {}
    print(f"Rendering 13 sections (ref={ref_image.name})...")
    for section_key, cfg in tokens["sections"].items():
        copy_data = copy.get(section_key, {})
        ref_images = [ref_image] if cfg["mode"] in ("image", "image_split") else []
        img = render_section(
            section_key=section_key,
            copy_data=copy_data,
            tokens=tokens,
            fonts_dir=FONTS_DIR,
            ref_images=ref_images,
        )
        out_path = out_dir / f"{section_key}.png"
        img.save(out_path, "PNG")
        section_paths[section_key] = out_path
        print(f"  ok {section_key:18s} {cfg['mode']:11s} {img.width}x{img.height}")

    final = out_dir / "final.png"
    stitch_sections(section_paths, final)
    print(f"\nDone: {final}  ({final.stat().st_size/1024:.0f} KB)")


if __name__ == "__main__":
    main()
