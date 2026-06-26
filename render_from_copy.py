"""카피 JSON을 받아 13섹션 상세페이지를 합성한다.

옵션 A 흐름: Claude(대화 세션)가 카피를 직접 작성 → JSON 저장 → 이 스크립트로 합성.

배경 이미지 소스 (우선순위):
  1. --ref <파일>      한 장을 모든 이미지 섹션에 사용 (빠른 확인용)
  2. --gemini          본사 룩북이 없을 때 Gemini 무료 티어로 섹션별 배경 생성
  3. (기본)            테스트용 샘플 배경

사용법:
    python render_from_copy.py <copy.json> [--ref 사진.jpg] [--gemini] [--out 폴더] [--brief brief.json]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from dotenv import load_dotenv

from pipeline.compose import render_section, load_tokens
from pipeline.stitch import stitch_sections

load_dotenv()

PROJECT = Path(__file__).parent
TOKENS_PATH = PROJECT / "design_tokens" / "premium-editorial.json"
FONTS_DIR = PROJECT / "fonts"
DEFAULT_REF = PROJECT / "tests" / "_fixtures" / "sample_ref.jpg"


def _parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="카피 JSON → 13섹션 상세페이지 합성")
    p.add_argument("copy_json", help="카피 JSON 경로")
    p.add_argument("--ref", help="모든 이미지 섹션에 쓸 배경 사진 한 장")
    p.add_argument("--gemini", action="store_true",
                   help="섹션별 배경을 Gemini 무료 티어로 생성")
    p.add_argument("--brief", help="브리프 JSON (Gemini 프롬프트용 brand/model/designer)")
    p.add_argument("--out", help="출력 폴더 (기본: <copy.json 위치>/render)")
    return p.parse_args(argv)


def _resolve_ref(section_key, cfg, args, brief, out_dir):
    """섹션 배경 이미지 경로를 결정한다 (룩북 → Gemini → 샘플 순)."""
    if cfg["mode"] not in ("image", "image_split"):
        return []
    if args.ref:
        return [Path(args.ref)]
    if args.gemini:
        from pipeline.image_gen import build_background_prompt, generate_background
        prompt = build_background_prompt(brief, section_key, cfg)
        bg_path = out_dir / "_bg" / f"{section_key}.png"
        if not bg_path.exists():
            print(f"     Gemini 배경 생성 중: {section_key}...")
            generate_background(prompt, bg_path)
        return [bg_path]
    return [DEFAULT_REF]


def main() -> None:
    args = _parse_args(sys.argv[1:])
    copy_path = Path(args.copy_json)
    out_dir = Path(args.out) if args.out else copy_path.parent / "render"
    brief = json.loads(Path(args.brief).read_text(encoding="utf-8")) if args.brief else {}

    copy = json.loads(copy_path.read_text(encoding="utf-8"))
    tokens = load_tokens(TOKENS_PATH)
    out_dir.mkdir(parents=True, exist_ok=True)

    src = "ref" if args.ref else ("gemini" if args.gemini else "sample")
    section_paths: dict[str, Path] = {}
    print(f"Rendering 13 sections (background source = {src})...")
    for section_key, cfg in tokens["sections"].items():
        copy_data = copy.get(section_key, {})
        ref_images = _resolve_ref(section_key, cfg, args, brief, out_dir)
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
