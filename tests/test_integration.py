"""모의 외부 API로 전체 파이프라인 1회 실행."""
import json
from pathlib import Path
from unittest.mock import MagicMock

from PIL import Image

from pipeline.library import LibraryRepository
from pipeline.copy import generate_copy
from pipeline.compose import render_section, load_tokens
from pipeline.stitch import stitch_sections


PROJECT_ROOT = Path(__file__).parent.parent
TOKENS_PATH = PROJECT_ROOT / "design_tokens" / "premium-editorial.json"
FONTS_DIR = PROJECT_ROOT / "fonts"
SAMPLE_INDEX = PROJECT_ROOT / "tests" / "_fixtures" / "sample_index.json"


def _mock_response(text):
    msg = MagicMock()
    msg.content = [MagicMock(text=text)]
    return msg


def test_full_pipeline(tmp_path):
    # 1. 모의 Drive 클라이언트 — 인덱스와 이미지 다운로드
    sample_image = tmp_path / "sample.jpg"
    Image.new("RGB", (1600, 1000), "#D0C0B0").save(sample_image)

    mock_drive = MagicMock()
    def fake_download(drive_id, mime_suffix=".jpg"):
        if drive_id == "INDEX_ID":
            return SAMPLE_INDEX
        return sample_image
    mock_drive.download.side_effect = fake_download

    # 2. 라이브러리에서 섹션별 이미지 매칭
    repo = LibraryRepository(
        drive=mock_drive, index_drive_id="INDEX_ID",
        cache_dir=tmp_path / "cache",
    )
    brief = {"brand": "B&B Italia", "model": "Charles",
             "designer": "Antonio Citterio"}
    matches = repo.find_for_section(brief, "01_hero")
    assert len(matches) >= 1

    # 3. 모의 Claude로 13섹션 카피 생성
    fake_copy = {
        f"section_{key}": {
            "headline_options": ["A", "B", "C"],
            "subheadline": "sub",
            "urgency_badge": "한정",
            "cta_text": "예약",
            "intro": "이런 고민",
            "pain_points": ["고민 1", "고민 2", "고민 3"],
            "emotional_hook": "..."
        }
        for key in [
            "01_hero", "02_pain", "03_problem", "04_story", "05_solution",
            "06_how_it_works", "07_social_proof", "08_authority",
            "09_benefits", "10_risk_removal", "11_comparison",
            "12_target_filter", "13_final_cta",
        ]
    }
    mock_client = MagicMock()
    mock_client.messages.create.return_value = _mock_response(
        json.dumps(fake_copy, ensure_ascii=False)
    )
    prompt_file = tmp_path / "03-copy.md"
    prompt_file.write_text("system", encoding="utf-8")
    copy_data = generate_copy(
        client=mock_client, brief=brief, research={},
        system_prompt_path=prompt_file,
    )
    assert len(copy_data) == 13

    # 4. 13섹션 렌더
    tokens = load_tokens(TOKENS_PATH)
    section_paths = {}
    out_dir = tmp_path / "render"
    out_dir.mkdir()
    for section_key, cfg in tokens["sections"].items():
        ref_paths = [sample_image] if cfg["mode"] in ("image", "image_split") else []
        img = render_section(
            section_key=section_key,
            copy_data=copy_data[f"section_{section_key}"],
            tokens=tokens, fonts_dir=FONTS_DIR, ref_images=ref_paths,
        )
        p = out_dir / f"{section_key}.png"
        img.save(p)
        section_paths[section_key] = p

    # 5. 합본
    final = tmp_path / "final.png"
    stitch_sections(section_paths, final)
    result = Image.open(final)
    assert result.width == 1200
    expected_height = sum(
        cfg["height"] for cfg in tokens["sections"].values()
    )
    assert result.height == expected_height  # 7,500px 부근
