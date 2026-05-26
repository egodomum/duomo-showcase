# DUOMO Landing Tool Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** DUOMO 내부 5~15명이 카페24/폐쇄몰용 1200px 너비 상세페이지 이미지를 1~2분 안에 만드는 사내 웹 도구를 1.5주 안에 MVP로 출시한다.

**Architecture:** Streamlit 단일 컨테이너를 Cloud Run에 배포. Google Workspace OAuth로 도메인 한정 인증. Google Drive를 본사 룩북 라이브러리 저장소로 사용. Claude API로 13섹션 카피 생성, PIL로 이미지·타이포 합성. AI 이미지 생성 의존성 없음.

**Tech Stack:** Python 3.11 · Streamlit · Pillow (PIL) · Anthropic SDK · Google API Client (Drive·OAuth) · pytest · Docker · Google Cloud Run

---

## 사전 준비 사항 (작업 시작 전)

다음을 미리 준비해야 합니다 (개발자가 직접 진행):

1. **Google Cloud 프로젝트** — Cloud Run, Drive API, OAuth 2.0 클라이언트 ID 발급
2. **Anthropic API 키** — https://console.anthropic.com 에서 발급
3. **DUOMO Google Workspace 관리자 권한** — OAuth 동의 화면 설정용
4. **폰트 파일 다운로드 준비**:
   - Pretendard (OFL): https://github.com/orioncactus/pretendard/releases (Pretendard-Light.otf, Pretendard-Medium.otf)
   - Playfair Display (OFL): https://fonts.google.com/specimen/Playfair+Display (PlayfairDisplay-Regular.ttf)

---

## Phase 1 — 프로젝트 기반 (Day 1)

### Task 1: 프로젝트 스캐폴딩

**Files:**
- Create: `requirements.txt`
- Create: `.gitignore`
- Create: `README.md`
- Create: `pipeline/__init__.py`
- Create: `storage/__init__.py`
- Create: `auth/__init__.py`
- Create: `tests/__init__.py`
- Create: `pages/` (디렉터리만, Streamlit 자동 인식)

- [ ] **Step 1: requirements.txt 작성**

Create `requirements.txt`:
```
streamlit==1.40.0
anthropic==0.39.0
google-api-python-client==2.150.0
google-auth==2.36.0
google-auth-oauthlib==1.2.1
google-auth-httplib2==0.2.0
Pillow==11.0.0
python-dotenv==1.0.1
pytest==8.3.4
pytest-mock==3.14.0
```

- [ ] **Step 2: .gitignore 작성**

Create `.gitignore`:
```
__pycache__/
*.pyc
.pytest_cache/
.env
.env.local
secrets/
.streamlit/secrets.toml
/tmp/
*.log
.venv/
venv/
output/
tests/_fixtures/.cache/
```

- [ ] **Step 3: README.md 작성**

Create `README.md`:
```markdown
# DUOMO Landing Tool

DUOMO 내부용 카페24 상세페이지 자동 생성 도구.

## 셋업 (로컬 개발)

```bash
python -m venv .venv
.venv\Scripts\activate           # Windows
pip install -r requirements.txt

# 환경변수 설정
copy .env.example .env
# .env에 ANTHROPIC_API_KEY, GOOGLE_OAUTH_CLIENT_ID, GOOGLE_OAUTH_CLIENT_SECRET, DRIVE_LOOKBOOK_FOLDER_ID, DRIVE_OUTPUT_FOLDER_ID, ALLOWED_DOMAIN 입력

streamlit run app.py
```

## 테스트

```bash
pytest tests/ -v
```

## 배포

상세는 `docs/superpowers/plans/2026-05-26-duomo-landing-tool.md` Phase 6 참조.
```

- [ ] **Step 4: 빈 __init__.py 4개 생성**

Create empty files:
- `pipeline/__init__.py`
- `storage/__init__.py`
- `auth/__init__.py`
- `tests/__init__.py`

각 파일 내용: 빈 파일 (한 줄 주석 한 줄: `"""Package."""`)

- [ ] **Step 5: pages 디렉터리 placeholder 생성**

Create `pages/.gitkeep` (빈 파일).

- [ ] **Step 6: 의존성 설치 확인**

Run: `python -m venv .venv && .venv\Scripts\activate && pip install -r requirements.txt`
Expected: 모든 패키지 충돌 없이 설치

- [ ] **Step 7: 커밋**

```bash
git add requirements.txt .gitignore README.md pipeline/__init__.py storage/__init__.py auth/__init__.py tests/__init__.py pages/.gitkeep
git commit -m "feat: project scaffolding"
```

---

### Task 2: 디자인 토큰 추출

**Files:**
- Create: `design_tokens/premium-editorial.json`

이 토큰은 [`~/.claude/skills/landing-page-generator/agents/04-design-direction.md`](../../../../../.claude/skills/landing-page-generator/agents/04-design-direction.md)의 `premium-editorial` 프리셋에서 추출.

- [ ] **Step 1: design_tokens/premium-editorial.json 작성**

Create `design_tokens/premium-editorial.json`:
```json
{
  "preset_name": "premium-editorial",
  "color": {
    "primary": "#1A1A1A",
    "secondary": "#3D3D3D",
    "accent": "#B8975A",
    "background": "#FAFAF7",
    "background_alt": "#1A1A1A",
    "text_primary": "#1A1A1A",
    "text_secondary": "#6B6B6B",
    "text_inverse": "#FAFAF7",
    "divider": "#B8975A",
    "muted": "#C9C3B8"
  },
  "typography": {
    "headline_serif": {
      "font_file": "PlayfairDisplay-Regular.ttf",
      "size_desktop": 60,
      "letter_spacing_ratio": -0.005,
      "line_height_ratio": 1.3
    },
    "headline_kr": {
      "font_file": "Pretendard-Light.otf",
      "size_desktop": 48,
      "letter_spacing_ratio": -0.005,
      "line_height_ratio": 1.3
    },
    "subheadline": {
      "font_file": "Pretendard-Light.otf",
      "size_desktop": 24,
      "letter_spacing_ratio": 0,
      "line_height_ratio": 1.5
    },
    "body": {
      "font_file": "Pretendard-Light.otf",
      "size_desktop": 17,
      "letter_spacing_ratio": 0,
      "line_height_ratio": 1.75
    },
    "cta": {
      "font_file": "Pretendard-Medium.otf",
      "size_desktop": 16,
      "letter_spacing_ratio": 0.06,
      "line_height_ratio": 1.4
    },
    "label_uppercase": {
      "font_file": "Pretendard-Medium.otf",
      "size_desktop": 13,
      "letter_spacing_ratio": 0.08,
      "line_height_ratio": 1.4
    },
    "brand_name": {
      "font_file": "PlayfairDisplay-Regular.ttf",
      "size_desktop": 48,
      "letter_spacing_ratio": 0.08,
      "line_height_ratio": 1.3
    }
  },
  "layout": {
    "max_width": 1200,
    "outer_padding_x": 72,
    "section_inner_padding_y": 80,
    "divider_width": 60,
    "divider_thickness": 1
  },
  "sections": {
    "01_hero":          { "height": 800, "mode": "image",        "background": "image_overlay_dark" },
    "02_pain":          { "height": 600, "mode": "typo",         "background": "off-white" },
    "03_problem":       { "height": 500, "mode": "typo",         "background": "dark" },
    "04_story":         { "height": 700, "mode": "image_split",  "background": "off-white" },
    "05_solution":      { "height": 400, "mode": "image",        "background": "off-white" },
    "06_how_it_works":  { "height": 600, "mode": "image",        "background": "off-white" },
    "07_social_proof":  { "height": 800, "mode": "typo",         "background": "dark" },
    "08_authority":     { "height": 500, "mode": "image",        "background": "off-white" },
    "09_benefits":      { "height": 700, "mode": "typo",         "background": "off-white" },
    "10_risk_removal":  { "height": 500, "mode": "typo",         "background": "off-white" },
    "11_comparison":    { "height": 400, "mode": "typo",         "background": "off-white" },
    "12_target_filter": { "height": 400, "mode": "typo",         "background": "off-white" },
    "13_final_cta":     { "height": 600, "mode": "image",        "background": "image_overlay_dark" }
  }
}
```

- [ ] **Step 2: JSON 파싱 검증**

Run: `python -c "import json; json.load(open('design_tokens/premium-editorial.json', encoding='utf-8')); print('OK')"`
Expected: `OK`

- [ ] **Step 3: 커밋**

```bash
git add design_tokens/premium-editorial.json
git commit -m "feat: add premium-editorial design tokens"
```

---

### Task 3: 프롬프트 자산 복사

**Files:**
- Create: `prompts/02-research.md`
- Create: `prompts/03-copy.md`
- Create: `prompts/04-design-direction.md`

[`~/.claude/skills/landing-page-generator/agents/`](../../../../../.claude/skills/landing-page-generator/agents/)에서 복사.

- [ ] **Step 1: prompts/ 디렉터리 생성 및 복사**

Run (PowerShell):
```powershell
New-Item -ItemType Directory -Force -Path "prompts" | Out-Null
Copy-Item -Path "$env:USERPROFILE\.claude\skills\landing-page-generator\agents\02-research.md" -Destination "prompts\02-research.md"
Copy-Item -Path "$env:USERPROFILE\.claude\skills\landing-page-generator\agents\03-copy.md" -Destination "prompts\03-copy.md"
Copy-Item -Path "$env:USERPROFILE\.claude\skills\landing-page-generator\agents\04-design-direction.md" -Destination "prompts\04-design-direction.md"
```

- [ ] **Step 2: 복사 확인**

Run: `Get-ChildItem prompts/` (PowerShell) 또는 `ls prompts/`
Expected: 3개 파일 (`02-research.md`, `03-copy.md`, `04-design-direction.md`)

- [ ] **Step 3: 커밋**

```bash
git add prompts/
git commit -m "feat: import DUOMO-tuned prompts from landing-page-generator skill"
```

---

### Task 4: 폰트 번들

**Files:**
- Create: `fonts/Pretendard-Light.otf`
- Create: `fonts/Pretendard-Medium.otf`
- Create: `fonts/PlayfairDisplay-Regular.ttf`
- Create: `fonts/README.md`

폰트 파일은 직접 다운로드 (사전 준비 §4 참조).

- [ ] **Step 1: fonts/ 디렉터리 생성**

Run: `mkdir fonts`

- [ ] **Step 2: 폰트 파일 다운로드 및 배치**

수동 작업:
1. https://github.com/orioncactus/pretendard/releases 에서 최신 릴리스의 `Pretendard-Light.otf`와 `Pretendard-Medium.otf` 다운로드 → `fonts/`로 이동
2. https://fonts.google.com/specimen/Playfair+Display 에서 "Download family" → 압축 해제 후 `PlayfairDisplay-Regular.ttf`만 `fonts/`로 이동

- [ ] **Step 3: fonts/README.md 작성 (라이선스 명시)**

Create `fonts/README.md`:
```markdown
# Bundled Fonts

| Font | License | Source |
|---|---|---|
| Pretendard-Light.otf | SIL Open Font License 1.1 | https://github.com/orioncactus/pretendard |
| Pretendard-Medium.otf | SIL Open Font License 1.1 | https://github.com/orioncactus/pretendard |
| PlayfairDisplay-Regular.ttf | SIL Open Font License 1.1 | https://fonts.google.com/specimen/Playfair+Display |

모든 폰트는 OFL 라이선스로 상업 사용·재배포 가능.
```

- [ ] **Step 4: 폰트 파일 확인**

Run:
```powershell
Get-ChildItem fonts/ | Select-Object Name, Length
```
Expected: 3개 .otf/.ttf 파일이 모두 존재, 각 100KB 이상

- [ ] **Step 5: 커밋**

```bash
git add fonts/
git commit -m "feat: bundle OFL fonts (Pretendard, Playfair Display)"
```

---

### Task 5: .env.example 작성

**Files:**
- Create: `.env.example`

- [ ] **Step 1: .env.example 작성**

Create `.env.example`:
```
# Anthropic API
ANTHROPIC_API_KEY=sk-ant-...

# Google OAuth 2.0
GOOGLE_OAUTH_CLIENT_ID=xxx.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=GOCSPX-...
GOOGLE_OAUTH_REDIRECT_URI=http://localhost:8501/_oauth_callback

# Google Drive (서비스 계정 또는 OAuth 사용자 토큰)
GOOGLE_SERVICE_ACCOUNT_JSON=secrets/service-account.json
DRIVE_LOOKBOOK_FOLDER_ID=
DRIVE_OUTPUT_FOLDER_ID=

# 인증 도메인
ALLOWED_DOMAIN=duomo.co.kr

# Streamlit
STREAMLIT_SERVER_PORT=8501
```

- [ ] **Step 2: 커밋**

```bash
git add .env.example
git commit -m "feat: add .env.example"
```

---

## Phase 2 — 라이브러리 & 저장소 (Day 2)

### Task 6: 인덱스 스키마 + 픽스처

**Files:**
- Create: `tests/_fixtures/sample_index.json`
- Create: `pipeline/library.py`

- [ ] **Step 1: 테스트용 샘플 인덱스 작성**

Create `tests/_fixtures/sample_index.json`:
```json
[
  {
    "id": "bbi-charles-living-001",
    "drive_id": "DRIVE_ID_001",
    "brand": "B&B Italia",
    "model": "Charles",
    "designer": "Antonio Citterio",
    "year": 1997,
    "type": "space",
    "section_fit": ["01_hero", "04_story", "13_final_cta"],
    "tags": ["modular", "sofa", "living", "natural-light"],
    "orientation": "landscape",
    "added_by": "admin@duomo.co.kr",
    "added_at": "2026-05-20"
  },
  {
    "id": "bbi-charles-product-001",
    "drive_id": "DRIVE_ID_002",
    "brand": "B&B Italia",
    "model": "Charles",
    "designer": "Antonio Citterio",
    "year": 1997,
    "type": "product",
    "section_fit": ["05_solution"],
    "tags": ["sofa", "isolated", "studio"],
    "orientation": "landscape",
    "added_by": "admin@duomo.co.kr",
    "added_at": "2026-05-20"
  },
  {
    "id": "cassina-lc4-living-001",
    "drive_id": "DRIVE_ID_003",
    "brand": "Cassina",
    "model": "LC4",
    "designer": "Le Corbusier",
    "year": 1928,
    "type": "space",
    "section_fit": ["01_hero", "04_story", "13_final_cta"],
    "tags": ["chaise", "iconic", "living"],
    "orientation": "landscape",
    "added_by": "admin@duomo.co.kr",
    "added_at": "2026-05-20"
  },
  {
    "id": "duomo-showroom-seoul-001",
    "drive_id": "DRIVE_ID_004",
    "brand": "DUOMO",
    "model": null,
    "designer": null,
    "year": null,
    "type": "showroom",
    "section_fit": ["08_authority", "06_how_it_works"],
    "tags": ["showroom", "seoul", "interior"],
    "orientation": "landscape",
    "added_by": "admin@duomo.co.kr",
    "added_at": "2026-05-20"
  }
]
```

- [ ] **Step 2: 커밋 (인덱스 픽스처)**

```bash
git add tests/_fixtures/sample_index.json
git commit -m "test: add sample library index fixture"
```

---

### Task 7: `load_index()` (TDD)

**Files:**
- Create: `tests/test_library.py`
- Create: `pipeline/library.py`

- [ ] **Step 1: 실패하는 테스트 작성**

Create `tests/test_library.py`:
```python
"""pipeline.library tests."""
from pathlib import Path

import pytest

from pipeline.library import load_index, LibraryIndexError

FIXTURE = Path(__file__).parent / "_fixtures" / "sample_index.json"


def test_load_index_returns_list_of_dicts():
    items = load_index(FIXTURE)
    assert isinstance(items, list)
    assert len(items) == 4
    assert items[0]["brand"] == "B&B Italia"


def test_load_index_validates_required_keys():
    """Missing 'id' should raise LibraryIndexError."""
    bad_file = FIXTURE.parent / "_bad_index.json"
    bad_file.write_text('[{"brand": "X"}]', encoding="utf-8")
    try:
        with pytest.raises(LibraryIndexError):
            load_index(bad_file)
    finally:
        bad_file.unlink()


def test_load_index_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        load_index(Path("/nonexistent.json"))
```

- [ ] **Step 2: 테스트 실패 확인**

Run: `pytest tests/test_library.py -v`
Expected: 3 FAIL — `ModuleNotFoundError: pipeline.library`

- [ ] **Step 3: `pipeline/library.py` 최소 구현**

Create `pipeline/library.py`:
```python
"""DUOMO 룩북 라이브러리 인덱스 로더와 검색 로직."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REQUIRED_KEYS = {"id", "brand", "type", "section_fit"}


class LibraryIndexError(Exception):
    """라이브러리 인덱스 무결성 오류."""


def load_index(path: Path) -> list[dict[str, Any]]:
    """JSON 인덱스 파일을 로드하고 필수 키를 검증한다.

    Raises:
        FileNotFoundError: 파일 없음
        LibraryIndexError: JSON 파싱 실패 또는 필수 키 누락
    """
    if not path.exists():
        raise FileNotFoundError(f"Index not found: {path}")

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise LibraryIndexError(f"Invalid JSON in {path}: {e}") from e

    if not isinstance(data, list):
        raise LibraryIndexError(f"Index must be a JSON array, got {type(data).__name__}")

    for i, item in enumerate(data):
        missing = REQUIRED_KEYS - set(item.keys())
        if missing:
            raise LibraryIndexError(
                f"Index item #{i} missing required keys: {sorted(missing)}"
            )

    return data
```

- [ ] **Step 4: 테스트 통과 확인**

Run: `pytest tests/test_library.py -v`
Expected: 3 PASS

- [ ] **Step 5: 커밋**

```bash
git add tests/test_library.py pipeline/library.py
git commit -m "feat: implement library index loader with validation"
```

---

### Task 8: `find_images_for_section()` 4단계 매칭 (TDD)

**Files:**
- Modify: `tests/test_library.py`
- Modify: `pipeline/library.py`

- [ ] **Step 1: 테스트 추가 (4단계 매칭 우선순위)**

Append to `tests/test_library.py`:
```python
from pipeline.library import find_images_for_section


def test_match_priority_1_brand_and_model_exact():
    items = load_index(FIXTURE)
    brief = {"brand": "B&B Italia", "model": "Charles", "designer": "Antonio Citterio"}
    result = find_images_for_section(items, brief, "01_hero")
    assert len(result) == 1
    assert result[0]["id"] == "bbi-charles-living-001"


def test_match_priority_2_brand_only_when_model_missing():
    items = load_index(FIXTURE)
    brief = {"brand": "B&B Italia", "model": "Maxalto", "designer": "Antonio Citterio"}
    # Maxalto는 인덱스에 없음, 브랜드 매칭으로 폴백
    result = find_images_for_section(items, brief, "01_hero")
    assert len(result) >= 1
    assert all(r["brand"] == "B&B Italia" for r in result)


def test_match_priority_3_designer_when_brand_missing():
    items = load_index(FIXTURE)
    brief = {"brand": "Unknown", "model": "X", "designer": "Antonio Citterio"}
    result = find_images_for_section(items, brief, "01_hero")
    assert len(result) >= 1
    assert all(r["designer"] == "Antonio Citterio" for r in result)


def test_match_priority_4_section_fit_only_when_all_else_missing():
    items = load_index(FIXTURE)
    brief = {"brand": "Z", "model": "Z", "designer": "Z"}
    result = find_images_for_section(items, brief, "01_hero")
    # 01_hero에 적합한 모든 이미지 반환
    assert len(result) >= 1
    assert all("01_hero" in r["section_fit"] for r in result)


def test_match_returns_empty_when_no_section_fit():
    items = load_index(FIXTURE)
    brief = {"brand": "Z", "model": "Z", "designer": "Z"}
    result = find_images_for_section(items, brief, "99_nonexistent")
    assert result == []


def test_match_respects_top_n_limit():
    items = load_index(FIXTURE)
    brief = {"brand": "Z", "model": "Z", "designer": "Z"}
    result = find_images_for_section(items, brief, "01_hero", top_n=1)
    assert len(result) == 1
```

- [ ] **Step 2: 테스트 실패 확인**

Run: `pytest tests/test_library.py -v`
Expected: 6개 새 테스트 FAIL — `ImportError: cannot import 'find_images_for_section'`

- [ ] **Step 3: 매칭 함수 구현**

Append to `pipeline/library.py`:
```python
def find_images_for_section(
    index: list[dict[str, Any]],
    brief: dict[str, Any],
    section_key: str,
    top_n: int = 5,
) -> list[dict[str, Any]]:
    """4단계 우선순위로 섹션에 적합한 이미지를 찾는다.

    1순위: brand + model 정확 매칭
    2순위: brand만 매칭
    3순위: designer 매칭
    4순위: section_fit만 매칭

    Args:
        index: load_index()로 로드한 라이브러리 인덱스
        brief: brand, model, designer 키를 가진 입력
        section_key: 예) "01_hero"
        top_n: 최대 반환 개수

    Returns:
        매칭된 이미지 메타데이터 리스트. 매칭 없으면 빈 리스트.
    """
    base = [i for i in index if section_key in i.get("section_fit", [])]
    if not base:
        return []

    brand = brief.get("brand")
    model = brief.get("model")
    designer = brief.get("designer")

    # 1순위: brand + model
    if brand and model:
        tier1 = [i for i in base if i.get("brand") == brand and i.get("model") == model]
        if tier1:
            return tier1[:top_n]

    # 2순위: brand만
    if brand:
        tier2 = [i for i in base if i.get("brand") == brand]
        if tier2:
            return tier2[:top_n]

    # 3순위: designer
    if designer:
        tier3 = [i for i in base if i.get("designer") == designer]
        if tier3:
            return tier3[:top_n]

    # 4순위: section_fit만 (base 그대로)
    return base[:top_n]
```

- [ ] **Step 4: 테스트 통과 확인**

Run: `pytest tests/test_library.py -v`
Expected: 9 PASS

- [ ] **Step 5: 커밋**

```bash
git add tests/test_library.py pipeline/library.py
git commit -m "feat: implement 4-tier image matching for sections"
```

---

### Task 9: `storage/drive.py` — Drive API 클라이언트 (TDD)

**Files:**
- Create: `tests/test_drive.py`
- Create: `storage/drive.py`

- [ ] **Step 1: 모의 Drive 클라이언트 테스트 작성**

Create `tests/test_drive.py`:
```python
"""storage.drive tests with mocked Google Drive API."""
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from storage.drive import DriveClient


def test_download_caches_file(tmp_path):
    """이미 캐시된 파일은 API 호출 없이 반환."""
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    cached_file = cache_dir / "DRIVE_ID_001.jpg"
    cached_file.write_bytes(b"cached-content")

    mock_service = MagicMock()
    client = DriveClient(service=mock_service, cache_dir=cache_dir)

    result = client.download("DRIVE_ID_001")

    assert result == cached_file
    assert result.read_bytes() == b"cached-content"
    mock_service.files().get_media.assert_not_called()


def test_download_fetches_when_not_cached(tmp_path):
    """캐시에 없으면 Drive API 호출."""
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()

    mock_service = MagicMock()
    # Drive API의 MediaIoBaseDownload 동작을 단순화: 직접 bytes 반환
    mock_request = MagicMock()
    mock_service.files().get_media.return_value = mock_request

    with patch("storage.drive.MediaIoBaseDownload") as mock_downloader_cls:
        mock_downloader = MagicMock()
        mock_downloader_cls.return_value = mock_downloader
        # next_chunk가 (status, done=True) 반환하도록
        mock_downloader.next_chunk.side_effect = [
            (MagicMock(progress=lambda: 1.0), True)
        ]
        # 다운로드 후 파일이 쓰여졌다고 가정 — buffer write를 시뮬레이션
        def fake_buffer_write(*args, **kwargs):
            (cache_dir / "DRIVE_ID_002.jpg").write_bytes(b"fresh-content")
            return mock_downloader

        mock_downloader_cls.side_effect = lambda buf, req: type(
            "FakeDl", (), {
                "next_chunk": lambda self: (
                    buf.write(b"fresh-content"),
                    (MagicMock(progress=lambda: 1.0), True)
                )[1]
            }
        )()

        client = DriveClient(service=mock_service, cache_dir=cache_dir)
        result = client.download("DRIVE_ID_002")

    assert result.exists()
    assert result.read_bytes() == b"fresh-content"
    mock_service.files().get_media.assert_called_with(fileId="DRIVE_ID_002")
```

- [ ] **Step 2: 테스트 실패 확인**

Run: `pytest tests/test_drive.py -v`
Expected: FAIL — `ModuleNotFoundError: storage.drive`

- [ ] **Step 3: `storage/drive.py` 구현**

Create `storage/drive.py`:
```python
"""Google Drive API 클라이언트 (다운로드·업로드·캐시)."""
from __future__ import annotations

import io
import logging
import time
from pathlib import Path
from typing import Optional

from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload

log = logging.getLogger(__name__)


class DriveError(Exception):
    """Drive API 호출 실패."""


class DriveClient:
    """Drive API 래퍼. 다운로드 결과는 cache_dir에 저장된다."""

    def __init__(self, service, cache_dir: Path):
        self.service = service
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def download(self, drive_id: str, mime_suffix: str = ".jpg") -> Path:
        """drive_id를 다운로드해서 cache_dir에 저장하고 경로를 반환한다.

        이미 캐시에 있으면 API 호출하지 않는다.
        실패 시 3회까지 지수 백오프 재시도.
        """
        cached = self.cache_dir / f"{drive_id}{mime_suffix}"
        if cached.exists():
            log.debug("cache hit: %s", drive_id)
            return cached

        last_err: Optional[Exception] = None
        for attempt in range(3):
            try:
                request = self.service.files().get_media(fileId=drive_id)
                buffer = io.BytesIO()
                downloader = MediaIoBaseDownload(buffer, request)
                done = False
                while not done:
                    _, done = downloader.next_chunk()
                cached.write_bytes(buffer.getvalue())
                return cached
            except Exception as e:
                last_err = e
                wait = 2 ** attempt
                log.warning("drive download failed (attempt %d): %s — retry in %ds",
                            attempt + 1, e, wait)
                time.sleep(wait)

        raise DriveError(f"Failed to download {drive_id} after 3 attempts: {last_err}")

    def upload(self, local_path: Path, parent_folder_id: str, name: Optional[str] = None) -> str:
        """로컬 파일을 Drive에 업로드하고 생성된 파일의 ID를 반환한다."""
        metadata = {
            "name": name or local_path.name,
            "parents": [parent_folder_id],
        }
        media = MediaFileUpload(str(local_path), resumable=True)
        try:
            created = self.service.files().create(
                body=metadata, media_body=media, fields="id"
            ).execute()
            return created["id"]
        except Exception as e:
            raise DriveError(f"Failed to upload {local_path}: {e}") from e
```

- [ ] **Step 4: 테스트 통과 확인**

Run: `pytest tests/test_drive.py -v`
Expected: 2 PASS

- [ ] **Step 5: 커밋**

```bash
git add tests/test_drive.py storage/drive.py
git commit -m "feat: implement Drive client with download cache and retry"
```

---

### Task 10: 인덱스 자동 새로고침 메커니즘

**Files:**
- Modify: `pipeline/library.py`
- Modify: `tests/test_library.py`

- [ ] **Step 1: 테스트 추가 (인덱스 새로고침)**

Append to `tests/test_library.py`:
```python
from unittest.mock import MagicMock, patch
from pipeline.library import LibraryRepository


def test_repository_loads_from_drive_on_first_access(tmp_path):
    """LibraryRepository는 첫 접근 시 Drive에서 _index.json을 가져온다."""
    cache_dir = tmp_path / "cache"
    mock_drive = MagicMock()
    # 모의: drive.download("INDEX_ID")가 fixture 파일 경로 반환
    mock_drive.download.return_value = FIXTURE

    repo = LibraryRepository(drive=mock_drive, index_drive_id="INDEX_ID",
                              cache_dir=cache_dir)
    items = repo.list_all()

    assert len(items) == 4
    mock_drive.download.assert_called_with("INDEX_ID", mime_suffix=".json")


def test_repository_caches_index_until_refresh(tmp_path):
    """두 번째 호출은 캐시 사용."""
    mock_drive = MagicMock()
    mock_drive.download.return_value = FIXTURE

    repo = LibraryRepository(drive=mock_drive, index_drive_id="INDEX_ID",
                              cache_dir=tmp_path / "cache")
    repo.list_all()
    repo.list_all()

    # download는 한 번만 호출되어야 함 (캐시 사용)
    assert mock_drive.download.call_count == 1
```

- [ ] **Step 2: 테스트 실패 확인**

Run: `pytest tests/test_library.py::test_repository_loads_from_drive_on_first_access -v`
Expected: FAIL — `cannot import LibraryRepository`

- [ ] **Step 3: `LibraryRepository` 구현**

Append to `pipeline/library.py`:
```python
class LibraryRepository:
    """Drive에서 인덱스를 로드하고 메모리 캐시한다."""

    def __init__(self, drive, index_drive_id: str, cache_dir: Path):
        self.drive = drive
        self.index_drive_id = index_drive_id
        self.cache_dir = cache_dir
        self._items: Optional[list[dict[str, Any]]] = None

    def list_all(self) -> list[dict[str, Any]]:
        """인덱스를 반환한다. 캐시되어 있지 않으면 Drive에서 가져옴."""
        if self._items is None:
            local_index = self.drive.download(self.index_drive_id, mime_suffix=".json")
            self._items = load_index(local_index)
        return self._items

    def refresh(self) -> None:
        """다음 list_all() 호출 시 Drive에서 다시 가져오도록 캐시 무효화."""
        self._items = None

    def find_for_section(self, brief: dict, section_key: str, top_n: int = 5
                         ) -> list[dict[str, Any]]:
        return find_images_for_section(self.list_all(), brief, section_key, top_n)
```

`pipeline/library.py` 상단에 추가 import: `from typing import Optional` (이미 있음).

- [ ] **Step 4: 테스트 통과 확인**

Run: `pytest tests/test_library.py -v`
Expected: 11 PASS

- [ ] **Step 5: 커밋**

```bash
git add pipeline/library.py tests/test_library.py
git commit -m "feat: add LibraryRepository with cached Drive index"
```

---

## Phase 3 — 카피 생성 (Day 3)

### Task 11: Claude 클라이언트 추상화 + 카피 생성 (TDD)

**Files:**
- Create: `tests/test_copy.py`
- Create: `pipeline/copy.py`

- [ ] **Step 1: 모의 Claude로 테스트 작성**

Create `tests/test_copy.py`:
```python
"""pipeline.copy tests with mocked Anthropic client."""
import json
from unittest.mock import MagicMock

import pytest

from pipeline.copy import generate_copy, CopyError


def _mock_response(text):
    msg = MagicMock()
    msg.content = [MagicMock(text=text)]
    return msg


def test_generate_copy_returns_dict(tmp_path):
    """카피 JSON 응답을 파싱해 dict로 반환."""
    fake_json = json.dumps({
        "section_01_hero": {
            "headline_options": ["a", "b", "c"],
            "subheadline": "sub",
            "urgency_badge": "한정",
            "cta_text": "예약"
        }
    }, ensure_ascii=False)

    mock_client = MagicMock()
    mock_client.messages.create.return_value = _mock_response(fake_json)

    prompt_file = tmp_path / "03-copy.md"
    prompt_file.write_text("system prompt", encoding="utf-8")

    result = generate_copy(
        client=mock_client,
        brief={"brand": "B&B Italia"},
        research={"persona": "consumer"},
        system_prompt_path=prompt_file,
        model="claude-sonnet-4-5",
    )

    assert "section_01_hero" in result
    assert result["section_01_hero"]["cta_text"] == "예약"


def test_generate_copy_retries_on_invalid_json(tmp_path):
    """첫 응답이 JSON 아니면 'JSON only' 메시지로 1회 재요청."""
    bad = _mock_response("어 그러니까... section_01은...")
    good = _mock_response(json.dumps({"section_01_hero": {"cta_text": "예약"}},
                                     ensure_ascii=False))

    mock_client = MagicMock()
    mock_client.messages.create.side_effect = [bad, good]

    prompt_file = tmp_path / "03-copy.md"
    prompt_file.write_text("system prompt", encoding="utf-8")

    result = generate_copy(
        client=mock_client,
        brief={}, research={},
        system_prompt_path=prompt_file,
        model="claude-sonnet-4-5",
    )

    assert result["section_01_hero"]["cta_text"] == "예약"
    assert mock_client.messages.create.call_count == 2


def test_generate_copy_raises_after_second_failure(tmp_path):
    """두 번 다 JSON 파싱 실패하면 CopyError."""
    bad = _mock_response("not json")
    mock_client = MagicMock()
    mock_client.messages.create.side_effect = [bad, bad]

    prompt_file = tmp_path / "03-copy.md"
    prompt_file.write_text("system", encoding="utf-8")

    with pytest.raises(CopyError):
        generate_copy(
            client=mock_client,
            brief={}, research={},
            system_prompt_path=prompt_file,
            model="claude-sonnet-4-5",
        )
```

- [ ] **Step 2: 테스트 실패 확인**

Run: `pytest tests/test_copy.py -v`
Expected: 3 FAIL — `ModuleNotFoundError: pipeline.copy`

- [ ] **Step 3: `pipeline/copy.py` 구현**

Create `pipeline/copy.py`:
```python
"""Claude API로 13섹션 카피 JSON 생성."""
from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)


class CopyError(Exception):
    """카피 생성 실패."""


def _extract_json(text: str) -> dict[str, Any]:
    """응답 텍스트에서 JSON 추출.

    1) 그대로 파싱 시도
    2) 첫 '{' 부터 마지막 '}' 까지 슬라이스 후 파싱
    """
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return json.loads(match.group(0))

    raise json.JSONDecodeError("No JSON found in response", text, 0)


def generate_copy(
    *,
    client,
    brief: dict[str, Any],
    research: dict[str, Any],
    system_prompt_path: Path,
    model: str = "claude-sonnet-4-5",
    max_tokens: int = 8000,
) -> dict[str, Any]:
    """13섹션 카피 JSON을 생성한다.

    응답이 JSON으로 파싱되지 않으면 'JSON only' 메시지를 추가해 1회 재요청.
    그래도 실패하면 CopyError.
    """
    system_prompt = system_prompt_path.read_text(encoding="utf-8")

    user_msg = (
        f"브리프:\n{json.dumps(brief, ensure_ascii=False, indent=2)}\n\n"
        f"리서치:\n{json.dumps(research, ensure_ascii=False, indent=2)}\n\n"
        "13섹션 카피 JSON을 생성해주세요. 출력은 JSON만, 다른 설명 없이."
    )

    for attempt in range(2):
        response = client.messages.create(
            model=model,
            system=system_prompt,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": user_msg}],
        )
        text = response.content[0].text
        try:
            return _extract_json(text)
        except json.JSONDecodeError as e:
            log.warning("copy JSON parse failed (attempt %d): %s", attempt + 1, e)
            user_msg = (
                "이전 응답이 JSON으로 파싱되지 않았습니다. "
                "**JSON만** 출력해주세요. 다른 텍스트·코드펜스 일체 금지.\n\n"
                + user_msg
            )

    raise CopyError("Failed to parse copy JSON after 2 attempts")
```

- [ ] **Step 4: 테스트 통과 확인**

Run: `pytest tests/test_copy.py -v`
Expected: 3 PASS

- [ ] **Step 5: 커밋**

```bash
git add tests/test_copy.py pipeline/copy.py
git commit -m "feat: implement Claude-based copy generation with JSON retry"
```

---

### Task 12: 리서치 + 디자인 방향 호출 (TDD)

**Files:**
- Modify: `pipeline/copy.py`
- Modify: `tests/test_copy.py`

리서치(`02-research.md`)와 디자인 방향(`04-design-direction.md`)도 같은 Claude 호출 패턴을 사용. DRY 원칙으로 공용 함수로 추출.

- [ ] **Step 1: 테스트 추가**

Append to `tests/test_copy.py`:
```python
from pipeline.copy import generate_research, generate_design_direction


def test_generate_research(tmp_path):
    fake_json = json.dumps({"persona": {"primary": "consumer"}}, ensure_ascii=False)
    mock_client = MagicMock()
    mock_client.messages.create.return_value = _mock_response(fake_json)

    prompt_file = tmp_path / "02-research.md"
    prompt_file.write_text("research system", encoding="utf-8")

    result = generate_research(
        client=mock_client,
        brief={"brand": "B&B Italia"},
        system_prompt_path=prompt_file,
    )
    assert result["persona"]["primary"] == "consumer"


def test_generate_design_direction(tmp_path):
    fake_json = json.dumps({"style_preset": "premium-editorial"}, ensure_ascii=False)
    mock_client = MagicMock()
    mock_client.messages.create.return_value = _mock_response(fake_json)

    prompt_file = tmp_path / "04-design.md"
    prompt_file.write_text("design system", encoding="utf-8")

    result = generate_design_direction(
        client=mock_client,
        brief={},
        research={},
        system_prompt_path=prompt_file,
    )
    assert result["style_preset"] == "premium-editorial"
```

- [ ] **Step 2: 테스트 실패 확인**

Run: `pytest tests/test_copy.py -v`
Expected: 2 FAIL — `cannot import generate_research, generate_design_direction`

- [ ] **Step 3: 공용 헬퍼 + 두 함수 추가**

Replace contents of `pipeline/copy.py`:
```python
"""Claude API로 리서치/카피/디자인 방향 JSON 생성."""
from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)


class CopyError(Exception):
    """Claude 응답 파싱 실패."""


def _extract_json(text: str) -> dict[str, Any]:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return json.loads(match.group(0))
    raise json.JSONDecodeError("No JSON found", text, 0)


def _call_with_retry(
    *,
    client,
    system_prompt: str,
    user_msg: str,
    model: str,
    max_tokens: int,
    label: str,
) -> dict[str, Any]:
    current = user_msg
    for attempt in range(2):
        response = client.messages.create(
            model=model,
            system=system_prompt,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": current}],
        )
        text = response.content[0].text
        try:
            return _extract_json(text)
        except json.JSONDecodeError as e:
            log.warning("%s JSON parse failed (attempt %d): %s", label, attempt + 1, e)
            current = (
                "이전 응답이 JSON으로 파싱되지 않았습니다. **JSON만** 출력해주세요. "
                "다른 텍스트·코드펜스 일체 금지.\n\n" + current
            )
    raise CopyError(f"Failed to parse {label} JSON after 2 attempts")


def generate_research(
    *,
    client,
    brief: dict[str, Any],
    system_prompt_path: Path,
    model: str = "claude-sonnet-4-5",
    max_tokens: int = 6000,
) -> dict[str, Any]:
    """02-research.md 시스템 프롬프트로 리서치 JSON 생성."""
    user_msg = (
        f"브리프:\n{json.dumps(brief, ensure_ascii=False, indent=2)}\n\n"
        "리서치 JSON을 생성해주세요. 출력은 JSON만."
    )
    return _call_with_retry(
        client=client,
        system_prompt=system_prompt_path.read_text(encoding="utf-8"),
        user_msg=user_msg,
        model=model,
        max_tokens=max_tokens,
        label="research",
    )


def generate_copy(
    *,
    client,
    brief: dict[str, Any],
    research: dict[str, Any],
    system_prompt_path: Path,
    model: str = "claude-sonnet-4-5",
    max_tokens: int = 8000,
) -> dict[str, Any]:
    """03-copy.md 시스템 프롬프트로 13섹션 카피 JSON 생성."""
    user_msg = (
        f"브리프:\n{json.dumps(brief, ensure_ascii=False, indent=2)}\n\n"
        f"리서치:\n{json.dumps(research, ensure_ascii=False, indent=2)}\n\n"
        "13섹션 카피 JSON을 생성해주세요. 출력은 JSON만."
    )
    return _call_with_retry(
        client=client,
        system_prompt=system_prompt_path.read_text(encoding="utf-8"),
        user_msg=user_msg,
        model=model,
        max_tokens=max_tokens,
        label="copy",
    )


def generate_design_direction(
    *,
    client,
    brief: dict[str, Any],
    research: dict[str, Any],
    system_prompt_path: Path,
    model: str = "claude-sonnet-4-5",
    max_tokens: int = 4000,
) -> dict[str, Any]:
    """04-design-direction.md 시스템 프롬프트로 디자인 방향 JSON 생성."""
    user_msg = (
        f"브리프:\n{json.dumps(brief, ensure_ascii=False, indent=2)}\n\n"
        f"리서치:\n{json.dumps(research, ensure_ascii=False, indent=2)}\n\n"
        "디자인 방향 JSON을 생성해주세요. 출력은 JSON만."
    )
    return _call_with_retry(
        client=client,
        system_prompt=system_prompt_path.read_text(encoding="utf-8"),
        user_msg=user_msg,
        model=model,
        max_tokens=max_tokens,
        label="design",
    )
```

- [ ] **Step 4: 테스트 통과 확인**

Run: `pytest tests/test_copy.py -v`
Expected: 5 PASS

- [ ] **Step 5: 커밋**

```bash
git add pipeline/copy.py tests/test_copy.py
git commit -m "feat: add research and design-direction generators (DRY)"
```

---

## Phase 4 — 합성 (Day 4~5)

### Task 13: 폰트 로더 + 디자인 토큰 로더 (TDD)

**Files:**
- Create: `tests/test_compose.py`
- Create: `pipeline/compose.py`

- [ ] **Step 1: 테스트 작성 (폰트 로더)**

Create `tests/test_compose.py`:
```python
"""pipeline.compose tests."""
from pathlib import Path

import pytest
from PIL import ImageFont

from pipeline.compose import load_tokens, load_font, FontError


PROJECT_ROOT = Path(__file__).parent.parent
TOKENS_PATH = PROJECT_ROOT / "design_tokens" / "premium-editorial.json"
FONTS_DIR = PROJECT_ROOT / "fonts"


def test_load_tokens():
    tokens = load_tokens(TOKENS_PATH)
    assert tokens["preset_name"] == "premium-editorial"
    assert tokens["color"]["accent"] == "#B8975A"
    assert tokens["sections"]["01_hero"]["height"] == 800


def test_load_font_returns_pil_font():
    tokens = load_tokens(TOKENS_PATH)
    font = load_font(tokens["typography"]["body"], fonts_dir=FONTS_DIR)
    assert isinstance(font, ImageFont.FreeTypeFont)


def test_load_font_raises_on_missing_file():
    fake_spec = {"font_file": "DoesNotExist.ttf", "size_desktop": 16,
                 "letter_spacing_ratio": 0, "line_height_ratio": 1.4}
    with pytest.raises(FontError):
        load_font(fake_spec, fonts_dir=FONTS_DIR)
```

- [ ] **Step 2: 테스트 실패 확인**

Run: `pytest tests/test_compose.py -v`
Expected: FAIL — `ModuleNotFoundError: pipeline.compose`

- [ ] **Step 3: `pipeline/compose.py` 시작**

Create `pipeline/compose.py`:
```python
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
```

- [ ] **Step 4: 테스트 통과 확인**

Run: `pytest tests/test_compose.py -v`
Expected: 3 PASS

- [ ] **Step 5: 커밋**

```bash
git add tests/test_compose.py pipeline/compose.py
git commit -m "feat: token and font loaders"
```

---

### Task 14: 텍스트 그리기 헬퍼 (TDD)

**Files:**
- Modify: `pipeline/compose.py`
- Modify: `tests/test_compose.py`

- [ ] **Step 1: 테스트 추가 (draw_text 헬퍼)**

Append to `tests/test_compose.py`:
```python
from PIL import Image
from pipeline.compose import draw_text


def test_draw_text_writes_pixels():
    """텍스트를 그리면 그 영역의 픽셀이 색상과 일치해야 한다."""
    tokens = load_tokens(TOKENS_PATH)
    img = Image.new("RGB", (400, 100), "#FFFFFF")
    draw_text(
        img,
        text="안녕",
        position=(20, 20),
        spec=tokens["typography"]["headline_kr"],
        color="#000000",
        fonts_dir=FONTS_DIR,
    )
    # 텍스트가 그려진 영역 어딘가에는 검정 픽셀이 있어야 함
    found_black = False
    for x in range(20, 200):
        for y in range(20, 80):
            r, g, b = img.getpixel((x, y))
            if r < 30 and g < 30 and b < 30:
                found_black = True
                break
        if found_black:
            break
    assert found_black, "draw_text가 픽셀을 그리지 않음"
```

- [ ] **Step 2: 테스트 실패 확인**

Run: `pytest tests/test_compose.py::test_draw_text_writes_pixels -v`
Expected: FAIL — `cannot import draw_text`

- [ ] **Step 3: draw_text 구현**

Append to `pipeline/compose.py`:
```python
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
```

- [ ] **Step 4: 테스트 통과 확인**

Run: `pytest tests/test_compose.py -v`
Expected: 4 PASS

- [ ] **Step 5: 커밋**

```bash
git add pipeline/compose.py tests/test_compose.py
git commit -m "feat: text drawing with letter-spacing + hairline divider"
```

---

### Task 15: 타이포 섹션 합성 — 그룹 B (TDD)

**Files:**
- Modify: `pipeline/compose.py`
- Modify: `tests/test_compose.py`

그룹 B 섹션 7개를 하나의 함수로 처리: Pain, Problem, Social Proof, Benefits, Risk Removal, Comparison, Target Filter.

- [ ] **Step 1: 테스트 추가**

Append to `tests/test_compose.py`:
```python
from pipeline.compose import render_typo_section


SAMPLE_COPY_PAIN = {
    "intro": "이런 고민, 익숙하지 않으세요?",
    "pain_points": [
        "백화점 가구는 어디나 비슷합니다",
        "병행 수입은 진품 보증이 불안합니다",
        "원하는 모델을 어디서 사야 할지 모릅니다",
    ],
    "emotional_hook": "공간이 평범해지는 이유는, 진짜를 만나지 못해서입니다.",
}


def test_render_typo_section_pain():
    tokens = load_tokens(TOKENS_PATH)
    img = render_typo_section(
        section_key="02_pain",
        copy_data=SAMPLE_COPY_PAIN,
        tokens=tokens,
        fonts_dir=FONTS_DIR,
    )
    assert img.size == (1200, 600)
    # off-white 배경: 모서리 픽셀이 거의 #FAFAF7
    r, g, b = img.getpixel((0, 0))
    assert r > 240 and g > 240 and b > 230


def test_render_typo_section_dark_mode():
    """03_problem은 dark 배경."""
    tokens = load_tokens(TOKENS_PATH)
    copy_data = {
        "hook": "당신 안목이 부족한 게 아닙니다",
        "reasons": ["이유 1", "이유 2", "이유 3"],
        "reframe": "결국 정식 수입 큐레이션이 답입니다.",
    }
    img = render_typo_section(
        section_key="03_problem",
        copy_data=copy_data,
        tokens=tokens,
        fonts_dir=FONTS_DIR,
    )
    r, g, b = img.getpixel((0, 0))
    # 다크 배경: #1A1A1A
    assert r < 50 and g < 50 and b < 50
```

- [ ] **Step 2: 테스트 실패 확인**

Run: `pytest tests/test_compose.py::test_render_typo_section_pain -v`
Expected: FAIL — `cannot import render_typo_section`

- [ ] **Step 3: render_typo_section 구현**

Append to `pipeline/compose.py`:
```python
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
```

- [ ] **Step 4: 테스트 통과 확인**

Run: `pytest tests/test_compose.py -v`
Expected: 6 PASS

- [ ] **Step 5: 커밋**

```bash
git add pipeline/compose.py tests/test_compose.py
git commit -m "feat: render typography sections (Pain/Problem/etc)"
```

---

### Task 16: 이미지 섹션 합성 — 그룹 A (TDD)

**Files:**
- Modify: `pipeline/compose.py`
- Modify: `tests/test_compose.py`

이미지 섹션 6개: Hero, Story, Solution, How It Works, Authority, Final CTA. 모두 배경 이미지 + 텍스트 오버레이 패턴.

- [ ] **Step 1: 테스트용 샘플 배경 이미지 생성**

Add helper at top of `tests/test_compose.py` (import 다음):
```python
SAMPLE_REF = PROJECT_ROOT / "tests" / "_fixtures" / "sample_ref.jpg"


@pytest.fixture(scope="module", autouse=True)
def _make_sample_ref():
    """테스트용 샘플 배경 이미지 생성."""
    if not SAMPLE_REF.exists():
        SAMPLE_REF.parent.mkdir(parents=True, exist_ok=True)
        # 1600x1000 베이지 그라데이션
        ref = Image.new("RGB", (1600, 1000), "#D9CFC0")
        for y in range(1000):
            r = int(217 - (y / 1000) * 40)
            g = int(207 - (y / 1000) * 35)
            b = int(192 - (y / 1000) * 30)
            for x in range(1600):
                ref.putpixel((x, y), (r, g, b))
        ref.save(SAMPLE_REF, "JPEG", quality=85)
    yield
```

- [ ] **Step 2: 테스트 추가**

Append to `tests/test_compose.py`:
```python
from pipeline.compose import render_image_section


SAMPLE_COPY_HERO = {
    "headline_options": [
        "30년이 지나도 사랑받는 소파, B&B Italia Charles",
        "Antonio Citterio가 1997년 그린 미니멀리즘의 정의",
        "이탈리아 공장에서 1주일에 단 8세트만 만들어지는 모듈러",
    ],
    "subheadline": "DUOMO가 정식 수입하는 정통 이탈리아 가구",
    "urgency_badge": "2026 봄 시즌 한정",
    "cta_text": "전시장 방문 예약",
}


def test_render_image_section_hero():
    tokens = load_tokens(TOKENS_PATH)
    img = render_image_section(
        section_key="01_hero",
        copy_data=SAMPLE_COPY_HERO,
        ref_image_path=SAMPLE_REF,
        tokens=tokens,
        fonts_dir=FONTS_DIR,
    )
    assert img.size == (1200, 800)
    # Hero는 dark overlay 적용되므로 평균 어둠
    pixels = [img.getpixel((x, y)) for x in (100, 600, 1100) for y in (100, 400, 700)]
    avg_brightness = sum(sum(p) for p in pixels) / (len(pixels) * 3)
    assert avg_brightness < 150  # overlay 적용 후 어두워야 함


def test_render_image_section_solution_no_overlay():
    """05_solution은 off-white 배경, dark overlay 없음."""
    tokens = load_tokens(TOKENS_PATH)
    copy = {
        "intro": "DUOMO PRESENTS",
        "product_name": "B&B Italia Charles",
        "one_liner": "미니멀리즘의 정의",
        "target_fit": "20평 이상 거실",
    }
    img = render_image_section(
        section_key="05_solution",
        copy_data=copy,
        ref_image_path=SAMPLE_REF,
        tokens=tokens,
        fonts_dir=FONTS_DIR,
    )
    assert img.size == (1200, 400)
```

- [ ] **Step 3: 테스트 실패 확인**

Run: `pytest tests/test_compose.py::test_render_image_section_hero -v`
Expected: FAIL — `cannot import render_image_section`

- [ ] **Step 4: render_image_section 구현**

Append to `pipeline/compose.py`:
```python
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
```

- [ ] **Step 5: 테스트 통과 확인**

Run: `pytest tests/test_compose.py -v`
Expected: 8 PASS

- [ ] **Step 6: 커밋**

```bash
git add pipeline/compose.py tests/test_compose.py
git commit -m "feat: render image-based sections with overlay"
```

---

### Task 17: 섹션 라우터 + 합본

**Files:**
- Modify: `pipeline/compose.py`
- Create: `pipeline/stitch.py`
- Modify: `tests/test_compose.py`

13섹션 모드(`image` / `typo` / `image_split`)에 따라 분기. Story(`04_story`)는 좌/우 이미지 split이지만 MVP에서는 단순화: ref가 1장이면 image 모드로, 2장이면 split.

- [ ] **Step 1: 섹션 라우터 테스트 작성**

Append to `tests/test_compose.py`:
```python
from pipeline.compose import render_section


def test_render_section_dispatches_image_mode():
    tokens = load_tokens(TOKENS_PATH)
    img = render_section(
        section_key="01_hero",
        copy_data=SAMPLE_COPY_HERO,
        tokens=tokens,
        fonts_dir=FONTS_DIR,
        ref_images=[SAMPLE_REF],
    )
    assert img.size == (1200, 800)


def test_render_section_dispatches_typo_mode():
    tokens = load_tokens(TOKENS_PATH)
    img = render_section(
        section_key="02_pain",
        copy_data=SAMPLE_COPY_PAIN,
        tokens=tokens,
        fonts_dir=FONTS_DIR,
        ref_images=[],
    )
    assert img.size == (1200, 600)


def test_render_section_image_mode_requires_ref():
    tokens = load_tokens(TOKENS_PATH)
    with pytest.raises(ComposeError):
        render_section(
            section_key="01_hero",
            copy_data=SAMPLE_COPY_HERO,
            tokens=tokens,
            fonts_dir=FONTS_DIR,
            ref_images=[],
        )
```

- [ ] **Step 2: 테스트 실패 확인**

Run: `pytest tests/test_compose.py -v`
Expected: 3 새 테스트 FAIL — `cannot import render_section`

- [ ] **Step 3: render_section 라우터 구현**

Append to `pipeline/compose.py` (`ComposeError`는 같은 파일 상단에 이미 정의되어 있으므로 별도 import 불필요):
```python
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
```

- [ ] **Step 4: 테스트 통과 확인**

Run: `pytest tests/test_compose.py -v`
Expected: 11 PASS

- [ ] **Step 5: stitch.py 작성**

Create `pipeline/stitch.py`:
```python
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
```

- [ ] **Step 6: stitch 간단 테스트 추가**

Create `tests/test_stitch.py`:
```python
from pathlib import Path
from PIL import Image

from pipeline.stitch import stitch_sections


def test_stitch_combines_sections(tmp_path):
    paths = {}
    for i, key in enumerate(["01_hero", "02_pain", "03_problem"]):
        p = tmp_path / f"{key}.png"
        Image.new("RGB", (1200, 200 + i * 100), "#FFFFFF").save(p)
        paths[key] = p

    out = tmp_path / "final.png"
    result = stitch_sections(paths, out)

    final = Image.open(result)
    assert final.width == 1200
    assert final.height == 200 + 300 + 400  # 200+300+400


def test_stitch_normalizes_width(tmp_path):
    paths = {"01_hero": tmp_path / "01.png"}
    Image.new("RGB", (1500, 800), "#FFF").save(paths["01_hero"])

    out = tmp_path / "final.png"
    result = stitch_sections(paths, out)

    final = Image.open(result)
    assert final.width == 1200
```

- [ ] **Step 7: 모든 테스트 통과 확인**

Run: `pytest tests/ -v`
Expected: 모두 PASS (라이브러리 11 + 드라이브 2 + 카피 5 + compose 11 + stitch 2 = 31)

- [ ] **Step 8: 커밋**

```bash
git add pipeline/compose.py pipeline/stitch.py tests/test_compose.py tests/test_stitch.py
git commit -m "feat: section router and 13-image stitcher"
```

---

## Phase 5 — Streamlit UI & 인증 (Day 6~7)

### Task 18: Google OAuth 모듈

**Files:**
- Create: `auth/google_oauth.py`
- Create: `tests/test_oauth.py`

- [ ] **Step 1: OAuth 모듈 테스트 작성 (도메인 검증)**

Create `tests/test_oauth.py`:
```python
import pytest

from auth.google_oauth import is_allowed_email, AuthError


def test_allowed_domain_passes():
    assert is_allowed_email("paul@duomo.co.kr", allowed_domain="duomo.co.kr") is True


def test_disallowed_domain_blocked():
    assert is_allowed_email("attacker@gmail.com", allowed_domain="duomo.co.kr") is False


def test_no_at_sign_raises():
    with pytest.raises(AuthError):
        is_allowed_email("not-an-email", allowed_domain="duomo.co.kr")


def test_case_insensitive_domain():
    assert is_allowed_email("paul@DUOMO.CO.KR", allowed_domain="duomo.co.kr") is True
```

- [ ] **Step 2: 테스트 실패 확인**

Run: `pytest tests/test_oauth.py -v`
Expected: 4 FAIL — `ModuleNotFoundError: auth.google_oauth`

- [ ] **Step 3: `auth/google_oauth.py` 구현**

Create `auth/google_oauth.py`:
```python
"""Google OAuth 2.0 + DUOMO 도메인 검증."""
from __future__ import annotations

import os
from typing import Optional

from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests as g_requests


class AuthError(Exception):
    """인증 실패."""


def is_allowed_email(email: str, allowed_domain: str) -> bool:
    """이메일 도메인이 allowed_domain과 일치하는지 검증한다."""
    if "@" not in email:
        raise AuthError(f"Not an email: {email}")
    domain = email.split("@", 1)[1].lower()
    return domain == allowed_domain.lower()


def build_flow(
    client_id: str,
    client_secret: str,
    redirect_uri: str,
    hd: Optional[str] = None,
) -> Flow:
    """OAuth 흐름 객체 생성. hd=도메인 힌트로 Workspace 한정 로그인 유도."""
    client_config = {
        "web": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [redirect_uri],
        }
    }
    flow = Flow.from_client_config(
        client_config,
        scopes=[
            "openid",
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/drive",
        ],
    )
    flow.redirect_uri = redirect_uri
    if hd:
        flow._authorization_url_kwargs = {"hd": hd}  # type: ignore[attr-defined]
    return flow


def verify_id_token(token: str, client_id: str) -> dict:
    """ID 토큰을 검증하고 페이로드를 반환한다."""
    try:
        payload = id_token.verify_oauth2_token(
            token, g_requests.Request(), client_id
        )
    except ValueError as e:
        raise AuthError(f"Invalid ID token: {e}") from e
    return payload
```

- [ ] **Step 4: 테스트 통과 확인**

Run: `pytest tests/test_oauth.py -v`
Expected: 4 PASS

- [ ] **Step 5: 커밋**

```bash
git add auth/google_oauth.py tests/test_oauth.py
git commit -m "feat: Google OAuth flow with domain restriction"
```

---

### Task 19: `app.py` — Streamlit 엔트리 + OAuth 가드

**Files:**
- Create: `app.py`

Streamlit은 OAuth 콜백을 native하게 지원하지 않으므로, MVP에서는 다음 단순 패턴 사용:
- 사용자가 첫 진입 → Streamlit이 OAuth URL을 보여줌
- 사용자 클릭 → Google에서 인증 → `?code=...`로 리다이렉트
- Streamlit이 `?code`를 받아 토큰 교환 → `st.session_state["user_email"]` 설정
- 도메인 검증 → 통과 시 정상 페이지, 실패 시 거부

- [ ] **Step 1: `app.py` 작성**

Create `app.py`:
```python
"""DUOMO Landing Tool — Streamlit 엔트리."""
from __future__ import annotations

import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from auth.google_oauth import build_flow, is_allowed_email, AuthError

load_dotenv()

CLIENT_ID = os.getenv("GOOGLE_OAUTH_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET")
REDIRECT_URI = os.getenv("GOOGLE_OAUTH_REDIRECT_URI", "http://localhost:8501")
ALLOWED_DOMAIN = os.getenv("ALLOWED_DOMAIN", "duomo.co.kr")

st.set_page_config(
    page_title="DUOMO Landing Tool",
    page_icon="📐",
    layout="wide",
)


def _gate_oauth() -> None:
    """OAuth 가드 — 미인증 사용자는 로그인 화면."""
    if st.session_state.get("user_email"):
        return

    if not (CLIENT_ID and CLIENT_SECRET):
        st.error("OAuth 환경변수가 설정되지 않았습니다. .env를 확인하세요.")
        st.stop()

    flow = build_flow(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, hd=ALLOWED_DOMAIN)

    query_params = st.query_params
    code = query_params.get("code")

    if not code:
        auth_url, _ = flow.authorization_url(prompt="select_account", hd=ALLOWED_DOMAIN)
        st.markdown("# DUOMO Landing Tool")
        st.markdown("DUOMO Workspace 계정으로 로그인하세요.")
        st.link_button("🔑 Google 로그인", auth_url, type="primary")
        st.stop()

    # 토큰 교환
    try:
        flow.fetch_token(code=code)
    except Exception as e:
        st.error(f"OAuth 토큰 교환 실패: {e}")
        st.stop()

    credentials = flow.credentials
    # ID 토큰에서 이메일 추출
    from auth.google_oauth import verify_id_token
    try:
        payload = verify_id_token(credentials.id_token, CLIENT_ID)
    except AuthError as e:
        st.error(f"인증 실패: {e}")
        st.stop()

    email = payload.get("email")
    if not email or not is_allowed_email(email, ALLOWED_DOMAIN):
        st.error(f"허용된 도메인이 아닙니다: {email}")
        st.stop()

    st.session_state["user_email"] = email
    st.session_state["credentials"] = credentials
    st.query_params.clear()
    st.rerun()


_gate_oauth()

st.sidebar.markdown(f"**{st.session_state['user_email']}**")
if st.sidebar.button("로그아웃"):
    st.session_state.clear()
    st.rerun()

st.title("DUOMO Landing Tool")
st.write("좌측 사이드바에서 페이지를 선택하세요.")
st.markdown("""
- **신규 프로젝트** — 새 상세페이지 만들기
- **최근 작업** — 지금까지 만든 페이지 목록
- **라이브러리 관리** — 본사 룩북 사진 업로드 (관리자)
""")
```

- [ ] **Step 2: 로컬 실행 시도**

(OAuth 환경변수 없이도 .env에 placeholder만 두면 로그인 화면이 보여야 함)

Run: `streamlit run app.py`
Expected: 브라우저에서 "OAuth 환경변수가 설정되지 않았습니다" 메시지 (placeholder 키일 경우) 또는 로그인 화면.

Ctrl+C로 종료.

- [ ] **Step 3: 커밋**

```bash
git add app.py
git commit -m "feat: Streamlit entry with OAuth gate"
```

---

### Task 20: `pages/1_new_project.py` — 입력 폼

**Files:**
- Create: `pages/1_new_project.py`

위저드의 첫 단계: 브리프 입력 + 레퍼런스 이미지 업로드.

- [ ] **Step 1: 입력 폼 페이지 작성**

Create `pages/1_new_project.py`:
```python
"""신규 프로젝트 위저드 — 입력 → 카피 검토 → 합성."""
from __future__ import annotations

import os
import json
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# 인증 확인 (app.py에서 세션에 user_email 세팅됨)
if not st.session_state.get("user_email"):
    st.error("먼저 로그인하세요.")
    st.page_link("app.py", label="홈으로")
    st.stop()

st.title("신규 프로젝트")

# 위저드 단계 관리
if "wizard_step" not in st.session_state:
    st.session_state.wizard_step = 1
if "brief" not in st.session_state:
    st.session_state.brief = {}
if "uploaded_refs" not in st.session_state:
    st.session_state.uploaded_refs = {}


def _step1_brief():
    st.header("1단계 · 브리프 입력")
    with st.form("brief_form"):
        col1, col2 = st.columns(2)
        with col1:
            brand = st.text_input("브랜드", value=st.session_state.brief.get("brand", ""),
                                  placeholder="예: B&B Italia")
            model = st.text_input("모델", value=st.session_state.brief.get("model", ""),
                                  placeholder="예: Charles")
            designer = st.text_input("디자이너",
                                     value=st.session_state.brief.get("designer", ""),
                                     placeholder="예: Antonio Citterio")
            year = st.text_input("디자인 연식",
                                 value=st.session_state.brief.get("year", ""),
                                 placeholder="예: 1997")
        with col2:
            one_liner = st.text_input("한 줄 정의",
                                      value=st.session_state.brief.get("one_liner", ""),
                                      placeholder="예: 미니멀리즘의 정의")
            target = st.text_input("타겟 고객",
                                   value=st.session_state.brief.get("target_audience", ""),
                                   placeholder="예: 자가 거주 30~50대")
            price_official = st.text_input(
                "공식가",
                value=st.session_state.brief.get("price_official", ""),
                placeholder="예: 18,400,000원~",
            )
            lead_time = st.text_input(
                "리드타임",
                value=st.session_state.brief.get("lead_time", ""),
                placeholder="예: 14~18주",
            )

        key_benefit = st.text_area(
            "핵심 가치 / 메시지",
            value=st.session_state.brief.get("key_benefit", ""),
            placeholder="예: 30년 가는 정통, 정식 수입 진품 보증, 5년 A/S",
        )
        urgency = st.text_input(
            "한정 요소",
            value=st.session_state.brief.get("urgency", ""),
            placeholder="예: 2026 봄 시즌 한정 패브릭, 국내 12세트",
        )

        st.markdown("---")
        st.subheader("레퍼런스 이미지 (선택)")
        st.caption(
            "라이브러리에 매칭이 안 되는 경우에만 업로드. 1~5장. "
            "본사 룩북 카탈로그·공간 사진을 권장."
        )
        uploads = st.file_uploader(
            "이미지 선택", type=["jpg", "jpeg", "png"],
            accept_multiple_files=True,
        )

        submitted = st.form_submit_button("카피 생성", type="primary")
        if submitted:
            if not brand or not model:
                st.error("브랜드와 모델은 필수입니다.")
                return
            st.session_state.brief = {
                "brand": brand, "model": model, "designer": designer,
                "year": year, "one_liner": one_liner,
                "target_audience": target, "price_official": price_official,
                "lead_time": lead_time, "key_benefit": key_benefit,
                "urgency": urgency,
            }
            # 업로드된 파일은 /tmp에 저장
            tmp_dir = Path("/tmp/duomo-uploads") / st.session_state["user_email"]
            tmp_dir.mkdir(parents=True, exist_ok=True)
            ref_paths = []
            for f in uploads:
                p = tmp_dir / f.name
                p.write_bytes(f.read())
                ref_paths.append(str(p))
            st.session_state.uploaded_refs = ref_paths
            st.session_state.wizard_step = 2
            st.rerun()


# Step 2, 3은 다음 task에서 추가
if st.session_state.wizard_step == 1:
    _step1_brief()
else:
    st.info(f"단계 {st.session_state.wizard_step} 구현은 다음 task에서.")
    if st.button("처음으로"):
        st.session_state.wizard_step = 1
        st.rerun()
```

- [ ] **Step 2: 로컬 실행 + UI 확인**

Run: `streamlit run app.py`
브라우저에서 좌측 사이드바 "1 new project" 클릭 → 입력 폼이 표시되어야 함.
Ctrl+C로 종료.

- [ ] **Step 3: 커밋**

```bash
git add pages/1_new_project.py
git commit -m "feat: new project wizard - step 1 brief form"
```

---

### Task 21: 위저드 Step 2 — 카피 생성 + 편집

**Files:**
- Modify: `pages/1_new_project.py`

- [ ] **Step 1: Claude 클라이언트 초기화 헬퍼 + Step 2 추가**

Replace last lines of `pages/1_new_project.py` (everything after `_step1_brief()` definition) with:

```python
import anthropic
from pipeline.copy import generate_research, generate_copy, generate_design_direction, CopyError

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


@st.cache_resource
def _claude_client():
    return anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def _step2_copy():
    st.header("2단계 · 카피 검토 및 편집")

    if "copy_data" not in st.session_state:
        client = _claude_client()
        with st.spinner("리서치 생성 중... (약 30초)"):
            try:
                research = generate_research(
                    client=client,
                    brief=st.session_state.brief,
                    system_prompt_path=PROMPTS_DIR / "02-research.md",
                )
                st.session_state.research = research
            except CopyError as e:
                st.error(f"리서치 생성 실패: {e}")
                return

        with st.spinner("카피 생성 중... (약 60초)"):
            try:
                copy_data = generate_copy(
                    client=client,
                    brief=st.session_state.brief,
                    research=st.session_state.research,
                    system_prompt_path=PROMPTS_DIR / "03-copy.md",
                )
                st.session_state.copy_data = copy_data
            except CopyError as e:
                st.error(f"카피 생성 실패: {e}")
                return

        with st.spinner("디자인 방향 결정 중..."):
            try:
                design = generate_design_direction(
                    client=client,
                    brief=st.session_state.brief,
                    research=st.session_state.research,
                    system_prompt_path=PROMPTS_DIR / "04-design-direction.md",
                )
                st.session_state.design = design
            except CopyError as e:
                st.error(f"디자인 방향 실패: {e}")
                return

    # 카피 편집 UI
    edited = {}
    for section_key, content in st.session_state.copy_data.items():
        with st.expander(f"📝 {section_key}", expanded=False):
            edited_content = {}
            for field, value in content.items():
                if isinstance(value, list):
                    text = "\n".join(value)
                    new_text = st.text_area(
                        field, value=text, key=f"{section_key}_{field}", height=80,
                    )
                    edited_content[field] = [
                        line for line in new_text.split("\n") if line.strip()
                    ]
                elif isinstance(value, dict):
                    st.json(value)
                    edited_content[field] = value
                else:
                    edited_content[field] = st.text_input(
                        field, value=str(value), key=f"{section_key}_{field}",
                    )
            edited[section_key] = edited_content

    col_a, col_b = st.columns([1, 1])
    with col_a:
        if st.button("← 브리프로 돌아가기"):
            st.session_state.wizard_step = 1
            del st.session_state["copy_data"]
            st.rerun()
    with col_b:
        if st.button("이미지 생성 →", type="primary"):
            st.session_state.copy_data = edited
            st.session_state.wizard_step = 3
            st.rerun()


# 라우팅
if st.session_state.wizard_step == 1:
    _step1_brief()
elif st.session_state.wizard_step == 2:
    _step2_copy()
else:
    st.info(f"단계 {st.session_state.wizard_step} 구현은 다음 task에서.")
    if st.button("처음으로"):
        st.session_state.wizard_step = 1
        for k in ["copy_data", "research", "design"]:
            st.session_state.pop(k, None)
        st.rerun()
```

- [ ] **Step 2: 로컬 실행 + 카피 생성 흐름 확인**

`ANTHROPIC_API_KEY`가 실제 키여야 함 (없으면 401 에러).
Run: `streamlit run app.py`
브리프 입력 → 카피 생성 → 13섹션 expander가 표시되어야 함.

- [ ] **Step 3: 커밋**

```bash
git add pages/1_new_project.py
git commit -m "feat: wizard step 2 - copy generation and editing"
```

---

### Task 22: 위저드 Step 3 — 이미지 매칭·선택·합성·미리보기·재생성

**Files:**
- Modify: `pages/1_new_project.py`

- [ ] **Step 1: Step 3 코드 추가**

Replace the `else: st.info(...)` block in `pages/1_new_project.py` with:

```python
from pipeline.library import LibraryRepository
from pipeline.compose import render_section, load_tokens
from pipeline.stitch import stitch_sections, SECTION_ORDER
from storage.drive import DriveClient

from googleapiclient.discovery import build as g_build


DRIVE_LOOKBOOK_INDEX_ID = os.getenv("DRIVE_LOOKBOOK_INDEX_ID")
DRIVE_OUTPUT_FOLDER_ID = os.getenv("DRIVE_OUTPUT_FOLDER_ID")
FONTS_DIR = Path(__file__).parent.parent / "fonts"
TOKENS_PATH = Path(__file__).parent.parent / "design_tokens" / "premium-editorial.json"


@st.cache_resource
def _drive_client():
    """현재 세션 credentials로 Drive 클라이언트 생성."""
    creds = st.session_state.get("credentials")
    if not creds:
        return None
    service = g_build("drive", "v3", credentials=creds)
    cache_dir = Path("/tmp/duomo-drive-cache")
    return DriveClient(service=service, cache_dir=cache_dir)


@st.cache_resource
def _library_repo():
    drive = _drive_client()
    if not drive or not DRIVE_LOOKBOOK_INDEX_ID:
        return None
    return LibraryRepository(
        drive=drive,
        index_drive_id=DRIVE_LOOKBOOK_INDEX_ID,
        cache_dir=Path("/tmp/duomo-library-cache"),
    )


def _step3_compose():
    st.header("3단계 · 이미지 선택 및 합성")
    tokens = load_tokens(TOKENS_PATH)
    repo = _library_repo()

    if "section_choices" not in st.session_state:
        # 이미지 섹션 자동 매칭 초기화
        st.session_state.section_choices = {}
        for section_key, cfg in tokens["sections"].items():
            if cfg["mode"] in ("image", "image_split"):
                if repo:
                    matches = repo.find_for_section(
                        st.session_state.brief, section_key, top_n=5,
                    )
                else:
                    matches = []
                st.session_state.section_choices[section_key] = {
                    "candidates": matches,
                    "selected_drive_id": matches[0]["drive_id"] if matches else None,
                    "uploaded_path": None,
                }

    # 이미지 섹션별 선택 UI
    for section_key, cfg in tokens["sections"].items():
        if cfg["mode"] not in ("image", "image_split"):
            continue
        with st.expander(f"🖼️ {section_key} (이미지)", expanded=False):
            choice = st.session_state.section_choices[section_key]
            if choice["candidates"]:
                labels = [f"{c['brand']} / {c.get('model','-')} / {c['id']}"
                          for c in choice["candidates"]]
                sel = st.radio(
                    "라이브러리에서 선택", labels, key=f"radio_{section_key}",
                    index=0,
                )
                sel_idx = labels.index(sel)
                choice["selected_drive_id"] = choice["candidates"][sel_idx]["drive_id"]
            else:
                st.warning("라이브러리 매칭 없음. 직접 업로드하세요.")
            upl = st.file_uploader(
                "또는 직접 업로드 (선택 시 라이브러리보다 우선)",
                type=["jpg", "jpeg", "png"], key=f"upl_{section_key}",
            )
            if upl:
                p = Path("/tmp/duomo-uploads") / st.session_state["user_email"] / f"{section_key}_{upl.name}"
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(upl.read())
                choice["uploaded_path"] = str(p)

    st.markdown("---")
    if st.button("🎨 13섹션 합성", type="primary"):
        _render_all_sections(tokens, repo)
        st.session_state.rendered = True

    if st.session_state.get("rendered"):
        _show_previews()
        st.markdown("---")
        if st.button("📦 합본 PNG 생성 + 다운로드", type="primary"):
            _stitch_and_offer_download()


def _render_all_sections(tokens, repo):
    drive = _drive_client()
    fonts_dir = FONTS_DIR
    out_dir = Path("/tmp/duomo-render") / st.session_state["user_email"]
    out_dir.mkdir(parents=True, exist_ok=True)
    st.session_state.rendered_paths = {}

    progress = st.progress(0.0)
    sections = list(tokens["sections"].items())
    for i, (section_key, cfg) in enumerate(sections):
        progress.progress((i + 1) / len(sections), text=f"렌더링 중: {section_key}")
        # 이미지 경로 결정
        ref_paths = []
        if cfg["mode"] in ("image", "image_split"):
            choice = st.session_state.section_choices.get(section_key, {})
            if choice.get("uploaded_path"):
                ref_paths = [Path(choice["uploaded_path"])]
            elif choice.get("selected_drive_id") and drive:
                ref_paths = [drive.download(choice["selected_drive_id"])]
        copy_data = st.session_state.copy_data.get(f"section_{section_key}", {})
        try:
            img = render_section(
                section_key=section_key,
                copy_data=copy_data,
                tokens=tokens,
                fonts_dir=fonts_dir,
                ref_images=ref_paths,
            )
            out_path = out_dir / f"{section_key}.png"
            img.save(out_path, "PNG")
            st.session_state.rendered_paths[section_key] = out_path
        except Exception as e:
            st.error(f"{section_key} 렌더링 실패: {e}")


def _show_previews():
    st.subheader("미리보기")
    for section_key in SECTION_ORDER:
        path = st.session_state.rendered_paths.get(section_key)
        if not path:
            continue
        col1, col2 = st.columns([4, 1])
        with col1:
            st.image(str(path), use_container_width=True, caption=section_key)
        with col2:
            if st.button(f"🔄 재생성", key=f"regen_{section_key}"):
                tokens = load_tokens(TOKENS_PATH)
                # 단일 섹션 재렌더
                cfg = tokens["sections"][section_key]
                drive = _drive_client()
                ref_paths = []
                if cfg["mode"] in ("image", "image_split"):
                    choice = st.session_state.section_choices.get(section_key, {})
                    if choice.get("uploaded_path"):
                        ref_paths = [Path(choice["uploaded_path"])]
                    elif choice.get("selected_drive_id") and drive:
                        ref_paths = [drive.download(choice["selected_drive_id"])]
                copy_data = st.session_state.copy_data.get(f"section_{section_key}", {})
                try:
                    img = render_section(
                        section_key=section_key, copy_data=copy_data,
                        tokens=tokens, fonts_dir=FONTS_DIR, ref_images=ref_paths,
                    )
                    img.save(path, "PNG")
                    st.rerun()
                except Exception as e:
                    st.error(f"재생성 실패: {e}")


def _stitch_and_offer_download():
    out = Path("/tmp/duomo-render") / st.session_state["user_email"] / "final.png"
    stitch_sections(st.session_state.rendered_paths, out)
    st.success(f"합본 생성 완료: {out}")
    with open(out, "rb") as f:
        st.download_button(
            "📥 합본 PNG 다운로드",
            data=f, file_name="duomo_landing.png", mime="image/png",
        )

    # Drive 자동 업로드
    drive = _drive_client()
    if drive and DRIVE_OUTPUT_FOLDER_ID:
        try:
            file_id = drive.upload(
                out, DRIVE_OUTPUT_FOLDER_ID,
                name=f"{st.session_state.brief.get('brand','x')}_{st.session_state.brief.get('model','x')}_landing.png",
            )
            st.info(f"Drive 업로드 완료: {file_id}")
        except Exception as e:
            st.warning(f"Drive 업로드 실패: {e}")


# 라우팅 업데이트
if st.session_state.wizard_step == 1:
    _step1_brief()
elif st.session_state.wizard_step == 2:
    _step2_copy()
elif st.session_state.wizard_step == 3:
    _step3_compose()
else:
    st.error(f"알 수 없는 단계: {st.session_state.wizard_step}")
    if st.button("처음으로"):
        for k in ["wizard_step", "copy_data", "research", "design",
                  "section_choices", "rendered", "rendered_paths"]:
            st.session_state.pop(k, None)
        st.rerun()
```

- [ ] **Step 2: 로컬 통합 테스트 (수동 QA)**

실제 환경변수 모두 설정한 상태에서:
Run: `streamlit run app.py`
브리프 입력 → 카피 생성 → 이미지 선택 → 합성 → 미리보기 → 합본 다운로드까지 흐름 확인.

(라이브러리가 비어 있어 매칭 실패하면 직접 업로드 흐름으로 검증)

- [ ] **Step 3: 커밋**

```bash
git add pages/1_new_project.py
git commit -m "feat: wizard step 3 - image matching, composition, regeneration"
```

---

### Task 23: `pages/2_history.py` — 최근 작업 목록

**Files:**
- Create: `pages/2_history.py`

MVP는 Drive 공유 폴더의 파일 목록만 표시. 검색·복제·메타데이터는 V2.

- [ ] **Step 1: 페이지 작성**

Create `pages/2_history.py`:
```python
"""최근 작업 — Drive 공유 폴더의 결과물 파일 목록."""
from __future__ import annotations

import os
from pathlib import Path

import streamlit as st
from googleapiclient.discovery import build as g_build

if not st.session_state.get("user_email"):
    st.error("먼저 로그인하세요.")
    st.stop()

DRIVE_OUTPUT_FOLDER_ID = os.getenv("DRIVE_OUTPUT_FOLDER_ID")

st.title("최근 작업")

creds = st.session_state.get("credentials")
if not creds or not DRIVE_OUTPUT_FOLDER_ID:
    st.warning("Drive 출력 폴더가 설정되지 않았습니다.")
    st.stop()

service = g_build("drive", "v3", credentials=creds)
results = service.files().list(
    q=f"'{DRIVE_OUTPUT_FOLDER_ID}' in parents and trashed = false",
    fields="files(id, name, modifiedTime, webViewLink)",
    orderBy="modifiedTime desc",
    pageSize=50,
).execute()

files = results.get("files", [])
if not files:
    st.info("아직 만들어진 페이지가 없습니다.")
else:
    for f in files:
        col1, col2, col3 = st.columns([3, 2, 1])
        with col1:
            st.write(f["name"])
        with col2:
            st.caption(f.get("modifiedTime", ""))
        with col3:
            st.link_button("열기", f["webViewLink"])
```

- [ ] **Step 2: 로컬 실행**

Run: `streamlit run app.py` → 좌측 "2 history" 클릭 → 출력 폴더가 비어 있으면 "아직 없음" 메시지.

- [ ] **Step 3: 커밋**

```bash
git add pages/2_history.py
git commit -m "feat: history page (Drive output folder listing)"
```

---

### Task 24: `pages/3_library_admin.py` — 라이브러리 관리자

**Files:**
- Create: `pages/3_library_admin.py`

- [ ] **Step 1: 페이지 작성**

Create `pages/3_library_admin.py`:
```python
"""라이브러리 관리자 — 본사 룩북 이미지 업로드 + 메타데이터 입력."""
from __future__ import annotations

import os
import json
from datetime import datetime
from pathlib import Path

import streamlit as st
from googleapiclient.discovery import build as g_build

from storage.drive import DriveClient
from pipeline.library import load_index

if not st.session_state.get("user_email"):
    st.error("먼저 로그인하세요.")
    st.stop()

DRIVE_LOOKBOOK_FOLDER_ID = os.getenv("DRIVE_LOOKBOOK_FOLDER_ID")
DRIVE_LOOKBOOK_INDEX_ID = os.getenv("DRIVE_LOOKBOOK_INDEX_ID")

st.title("라이브러리 관리")
st.caption("본사 룩북·DUOMO 자체 촬영 사진을 업로드하고 인덱스에 등록합니다.")

if not (DRIVE_LOOKBOOK_FOLDER_ID and DRIVE_LOOKBOOK_INDEX_ID):
    st.error("DRIVE_LOOKBOOK_FOLDER_ID, DRIVE_LOOKBOOK_INDEX_ID 환경변수 설정 필요")
    st.stop()

creds = st.session_state.get("credentials")
service = g_build("drive", "v3", credentials=creds)
drive = DriveClient(
    service=service, cache_dir=Path("/tmp/duomo-library-cache"),
)


def _load_index_from_drive() -> list[dict]:
    local = drive.download(DRIVE_LOOKBOOK_INDEX_ID, mime_suffix=".json")
    return load_index(local)


def _save_index_to_drive(items: list[dict]) -> None:
    """인덱스 JSON을 Drive에 업데이트."""
    tmp = Path("/tmp/_index.json")
    tmp.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
    from googleapiclient.http import MediaFileUpload
    media = MediaFileUpload(str(tmp), mimetype="application/json")
    service.files().update(fileId=DRIVE_LOOKBOOK_INDEX_ID, media_body=media).execute()


tab1, tab2 = st.tabs(["새 이미지 추가", "기존 인덱스 보기"])

with tab1:
    with st.form("library_upload"):
        st.subheader("이미지 + 메타데이터 입력")
        col1, col2 = st.columns(2)
        with col1:
            brand = st.text_input("브랜드 *", placeholder="B&B Italia")
            model = st.text_input("모델", placeholder="Charles")
            designer = st.text_input("디자이너", placeholder="Antonio Citterio")
            year = st.number_input("디자인 연식", min_value=1900, max_value=2100,
                                   value=2000, step=1)
        with col2:
            img_type = st.selectbox("타입 *",
                                    ["space", "product", "detail", "showroom"])
            orientation = st.selectbox("방향", ["landscape", "portrait", "square"])
            section_fit = st.multiselect(
                "적합 섹션 *",
                ["01_hero", "04_story", "05_solution", "06_how_it_works",
                 "08_authority", "13_final_cta"],
            )
            tags_text = st.text_input("태그 (콤마 구분)",
                                      placeholder="modular, sofa, living")

        file = st.file_uploader("이미지 파일 *", type=["jpg", "jpeg", "png"])
        submitted = st.form_submit_button("Drive에 업로드 + 인덱스 등록",
                                          type="primary")
        if submitted:
            if not (brand and img_type and section_fit and file):
                st.error("필수 항목(* 표시) 입력 필요")
            else:
                tmp = Path("/tmp/upload") / file.name
                tmp.parent.mkdir(parents=True, exist_ok=True)
                tmp.write_bytes(file.read())
                with st.spinner("Drive 업로드 중..."):
                    drive_id = drive.upload(tmp, DRIVE_LOOKBOOK_FOLDER_ID,
                                            name=file.name)
                item_id = f"{brand.lower().replace(' ', '-')}-{(model or 'x').lower()}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                new_item = {
                    "id": item_id,
                    "drive_id": drive_id,
                    "brand": brand,
                    "model": model or None,
                    "designer": designer or None,
                    "year": int(year) if year else None,
                    "type": img_type,
                    "section_fit": section_fit,
                    "tags": [t.strip() for t in tags_text.split(",") if t.strip()],
                    "orientation": orientation,
                    "added_by": st.session_state["user_email"],
                    "added_at": datetime.now().strftime("%Y-%m-%d"),
                }
                with st.spinner("인덱스 업데이트 중..."):
                    items = _load_index_from_drive()
                    items.append(new_item)
                    _save_index_to_drive(items)
                st.success(f"등록 완료: {item_id}")

with tab2:
    items = _load_index_from_drive()
    st.info(f"총 {len(items)}장 등록")
    for it in items[-20:]:
        st.write(f"**{it['brand']}** / {it.get('model','-')} — {it['type']} — "
                 f"적합섹션 {it['section_fit']} — by {it['added_by']}")
```

- [ ] **Step 2: 로컬 실행 + 1장 업로드 시도**

실제 Drive 폴더 ID·인덱스 파일 ID가 설정된 상태에서 테스트.
Run: `streamlit run app.py`
"3 library admin" → 메타데이터 입력 + 이미지 업로드 → "등록 완료" 메시지 확인.

- [ ] **Step 3: 커밋**

```bash
git add pages/3_library_admin.py
git commit -m "feat: library admin page (upload + index update)"
```

---

## Phase 6 — 통합·배포 (Day 8)

### Task 25: 통합 테스트 (모의 Drive + 모의 Claude)

**Files:**
- Create: `tests/test_integration.py`

- [ ] **Step 1: End-to-end 흐름 통합 테스트 작성**

Create `tests/test_integration.py`:
```python
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
```

- [ ] **Step 2: 통합 테스트 통과 확인**

Run: `pytest tests/test_integration.py -v`
Expected: 1 PASS (작업 ~10초 — 13섹션 렌더)

- [ ] **Step 3: 전체 테스트 통과 확인**

Run: `pytest tests/ -v`
Expected: 모든 테스트 (~33개) PASS

- [ ] **Step 4: 커밋**

```bash
git add tests/test_integration.py
git commit -m "test: full pipeline integration test with mocks"
```

---

### Task 26: Dockerfile 작성

**Files:**
- Create: `Dockerfile`
- Create: `.dockerignore`

- [ ] **Step 1: Dockerfile 작성**

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 시스템 의존성 (Pillow에 필요한 라이브러리)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg-dev \
    zlib1g-dev \
    libfreetype6-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py ./
COPY pages/ ./pages/
COPY pipeline/ ./pipeline/
COPY storage/ ./storage/
COPY auth/ ./auth/
COPY prompts/ ./prompts/
COPY design_tokens/ ./design_tokens/
COPY fonts/ ./fonts/

ENV PORT=8501
ENV PYTHONUNBUFFERED=1

EXPOSE 8501

CMD ["streamlit", "run", "app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--browser.gatherUsageStats=false"]
```

- [ ] **Step 2: .dockerignore 작성**

Create `.dockerignore`:
```
.git/
__pycache__/
*.pyc
.pytest_cache/
.env
.env.local
secrets/
tests/
docs/
.venv/
venv/
*.log
output/
.streamlit/
```

- [ ] **Step 3: 로컬 빌드 + 실행 테스트**

Run:
```bash
docker build -t duomo-landing-tool:dev .
docker run --rm -p 8501:8501 \
  -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
  -e GOOGLE_OAUTH_CLIENT_ID=$GOOGLE_OAUTH_CLIENT_ID \
  -e GOOGLE_OAUTH_CLIENT_SECRET=$GOOGLE_OAUTH_CLIENT_SECRET \
  -e GOOGLE_OAUTH_REDIRECT_URI=http://localhost:8501 \
  -e ALLOWED_DOMAIN=duomo.co.kr \
  duomo-landing-tool:dev
```

브라우저에서 http://localhost:8501 접속 → 로그인 화면 확인.

- [ ] **Step 4: 커밋**

```bash
git add Dockerfile .dockerignore
git commit -m "feat: Dockerfile for Cloud Run deployment"
```

---

### Task 27: Cloud Run 배포 스크립트 + 문서

**Files:**
- Create: `deploy/deploy.sh`
- Create: `deploy/README.md`

- [ ] **Step 1: 배포 스크립트 작성**

Create `deploy/deploy.sh`:
```bash
#!/usr/bin/env bash
set -euo pipefail

# 사전 조건:
# - gcloud CLI 설치 + auth login 완료
# - GCP 프로젝트에 Cloud Run, Artifact Registry, Drive API 활성화
# - 환경변수 설정: PROJECT_ID, REGION (기본 asia-northeast3)

PROJECT_ID="${PROJECT_ID:?Set PROJECT_ID env var}"
REGION="${REGION:-asia-northeast3}"
SERVICE="duomo-landing-tool"
IMAGE="$REGION-docker.pkg.dev/$PROJECT_ID/duomo/$SERVICE:$(git rev-parse --short HEAD)"

echo "Building image: $IMAGE"
gcloud builds submit --tag "$IMAGE" --project "$PROJECT_ID"

echo "Deploying to Cloud Run..."
gcloud run deploy "$SERVICE" \
    --image "$IMAGE" \
    --region "$REGION" \
    --project "$PROJECT_ID" \
    --platform managed \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 1 \
    --min-instances 0 \
    --max-instances 3 \
    --timeout 3600 \
    --set-secrets="ANTHROPIC_API_KEY=anthropic-key:latest,GOOGLE_OAUTH_CLIENT_SECRET=oauth-secret:latest" \
    --set-env-vars="GOOGLE_OAUTH_CLIENT_ID=$GOOGLE_OAUTH_CLIENT_ID,GOOGLE_OAUTH_REDIRECT_URI=$GOOGLE_OAUTH_REDIRECT_URI,ALLOWED_DOMAIN=$ALLOWED_DOMAIN,DRIVE_LOOKBOOK_FOLDER_ID=$DRIVE_LOOKBOOK_FOLDER_ID,DRIVE_LOOKBOOK_INDEX_ID=$DRIVE_LOOKBOOK_INDEX_ID,DRIVE_OUTPUT_FOLDER_ID=$DRIVE_OUTPUT_FOLDER_ID"

echo "Done. URL:"
gcloud run services describe "$SERVICE" --region "$REGION" --project "$PROJECT_ID" \
    --format='value(status.url)'
```

- [ ] **Step 2: 배포 문서 작성**

Create `deploy/README.md`:
```markdown
# Cloud Run 배포

## 사전 준비

1. **GCP 프로젝트 생성** (예: `duomo-internal`)
2. **API 활성화**:
   ```bash
   gcloud services enable run.googleapis.com \
       artifactregistry.googleapis.com \
       cloudbuild.googleapis.com \
       drive.googleapis.com
   ```
3. **Artifact Registry 리포 생성**:
   ```bash
   gcloud artifacts repositories create duomo \
       --repository-format=docker --location=asia-northeast3
   ```
4. **OAuth 2.0 클라이언트 생성** (GCP Console > APIs & Services > Credentials):
   - Authorized redirect URIs에 Cloud Run URL 추가 (예: `https://duomo-landing-tool-xxx.run.app`)
   - 동의 화면을 "Internal" (Workspace 한정)로 설정
5. **Secret 등록**:
   ```bash
   echo -n "sk-ant-..." | gcloud secrets create anthropic-key --data-file=-
   echo -n "GOCSPX-..." | gcloud secrets create oauth-secret --data-file=-
   ```
6. **Drive에 폴더·인덱스 파일 생성**:
   - `/duomo/lookbook/` 공유 폴더 → ID를 `DRIVE_LOOKBOOK_FOLDER_ID` 로
   - 폴더 안에 빈 `_index.json` (내용: `[]`) → ID를 `DRIVE_LOOKBOOK_INDEX_ID` 로
   - `/duomo/landing-output/` 공유 폴더 → ID를 `DRIVE_OUTPUT_FOLDER_ID` 로

## 배포

```bash
export PROJECT_ID=duomo-internal
export GOOGLE_OAUTH_CLIENT_ID=xxx.apps.googleusercontent.com
export GOOGLE_OAUTH_REDIRECT_URI=https://duomo-landing-tool-xxx.run.app
export ALLOWED_DOMAIN=duomo.co.kr
export DRIVE_LOOKBOOK_FOLDER_ID=...
export DRIVE_LOOKBOOK_INDEX_ID=...
export DRIVE_OUTPUT_FOLDER_ID=...

bash deploy/deploy.sh
```

## 첫 배포 후

1. Cloud Run URL을 OAuth 클라이언트의 redirect URI에 등록 (Console에서 수정)
2. 두 번째 배포로 redirect_uri 확정
```

- [ ] **Step 3: 권한 설정 (Windows에서는 git 속성으로 처리)**

```bash
git add deploy/deploy.sh
git update-index --chmod=+x deploy/deploy.sh
```

(Windows에서는 위 명령으로 git에는 +x 권한이 기록됨)

- [ ] **Step 4: 커밋**

```bash
git add deploy/
git commit -m "feat: Cloud Run deployment script and docs"
```

---

## Phase 7 — QA & 런칭 (Day 9~10)

### Task 28: 라이브러리 초기 30~50장 업로드

**Files:** (코드 변경 없음 — 운영 작업)

- [ ] **Step 1: 우선순위 입고 라인업 식별**

마케팅 팀과 함께 가장 자주 다룰 5~10개 모델 식별 (예시):
- B&B Italia: Charles, Tufty-Time, Diesis
- Cassina: LC4, 671, Maralunga
- Flos: Arco, IC Lights
- Artemide: Tolomeo, Tizio

- [ ] **Step 2: 본사 룩북 사진 수집**

각 모델당 3~5장 (space, product, detail 다양하게).
선택 기준:
- 1600×1000 이상 고해상도
- 자연광·매거진 톤
- 한글 텍스트가 들어가지 않은 깨끗한 컷

- [ ] **Step 3: 라이브러리 관리자 페이지로 업로드**

배포된 Cloud Run URL에서 로그인 → 라이브러리 관리 → 한 장씩 메타데이터 입력하며 업로드.
총 30~50장 등록.

- [ ] **Step 4: 인덱스 검증**

새 프로젝트 페이지에서 "B&B Italia Charles" 입력 → 라이브러리 매칭 결과가 정확한지 확인.

### Task 29: 실제 DUOMO 신상 3건 수동 QA

**Files:** (코드 변경 없음)

- [ ] **Step 1: 테스트 케이스 선정**

각 카테고리 1건씩:
1. **소파** — B&B Italia Charles
2. **셰이즈** — Cassina LC4
3. **조명** — Flos Arco

- [ ] **Step 2: 각 건에 대해 전체 흐름 실행**

각 케이스마다:
1. 브리프 입력 (실제 정보 — 가격·리드타임·디자이너·연식 정확히)
2. 카피 생성 → 편집 검토
3. 이미지 자동 매칭 결과 확인
4. 합성 → 합본 다운로드
5. **디자이너에게 결과 보여주고 코멘트 받기**

- [ ] **Step 3: 발견된 이슈 기록**

`docs/superpowers/qa/2026-XX-XX-launch-qa.md`에 케이스별 이슈·개선점 기록.

### Task 30: 런칭 체크리스트

**Files:**
- Create: `docs/superpowers/launch-checklist.md`

- [ ] **Step 1: 체크리스트 작성**

Create `docs/superpowers/launch-checklist.md`:
```markdown
# Launch Checklist

## 인프라
- [ ] Cloud Run 배포 완료, public URL 확인
- [ ] OAuth redirect URI에 Cloud Run URL 등록
- [ ] Secret Manager에 ANTHROPIC_API_KEY, GOOGLE_OAUTH_CLIENT_SECRET 등록
- [ ] Drive 공유 폴더 3개 생성·권한 부여 (lookbook, output, index file)
- [ ] 환경변수 7개 모두 Cloud Run에 설정

## 라이브러리
- [ ] 초기 30~50장 업로드 완료
- [ ] 매칭 검증 3건 완료 (각 브랜드별 1건)

## 사내 안내
- [ ] DUOMO 팀에 도구 사용법 1페이지 안내 문서 공유
- [ ] 첫 사용자 3명 대상 시연 (마케팅·영업·디자이너 1명씩)
- [ ] 피드백 수집 채널 결정 (Slack 채널 또는 별도)

## 운영
- [ ] Cloud Run 로그 모니터링 셋업 (월 비용 알림 포함)
- [ ] 관리자 권한 부여 (라이브러리 업로드 가능 사용자)
- [ ] 1주 후 정기 회고 일정 잡기
```

- [ ] **Step 2: 커밋**

```bash
git add docs/superpowers/launch-checklist.md
git commit -m "docs: launch checklist"
```

---

## 완료 기준

- [ ] 모든 33개 단위 테스트 통과
- [ ] 통합 테스트 1개 통과
- [ ] 실제 DUOMO 신상 3건으로 수동 QA 완료
- [ ] 디자이너 검수 OK (디자인 토큰 조정 반영)
- [ ] Cloud Run 배포 + OAuth 로그인 작동
- [ ] 룩북 라이브러리 30~50장 등록
- [ ] 런칭 체크리스트 모든 항목 완료
