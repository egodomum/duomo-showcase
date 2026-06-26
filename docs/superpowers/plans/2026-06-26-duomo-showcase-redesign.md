# DUOMO Showcase Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 기존 13섹션 퍼널 도구를 DUOMO Figma 톤(1000px·중앙·순백·브랜드컬러·쇼케이스)의 HTML/CSS 블록 레지스트리 생성기로 재구축한다.

**Architecture:** 각 섹션 = 자족 "블록"(HTML 조각을 반환하는 모듈). 사용자가 블록을 순서대로 조립한 recipe → page_builder가 1000px HTML로 결합 → Playwright 헤드리스로 full_page PNG 캡처. 토큰·브랜드 액센트는 CSS 변수로 주입. 카피는 Claude가 블록 단위로 생성(쇼케이스 톤, 퍼널 금지).

**Tech Stack:** Python 3.14 · Playwright(Chromium) · Jinja 불필요(f-string HTML) · Pillow(검증용) · Anthropic SDK · Streamlit · pytest

---

## 사전 상태 (이미 완료, 재실행 불필요)

- ✅ `fonts/*.woff2` 5종 (Pretendard Regular/Medium/SemiBold/Light + NotoSerifDisplay-SemiBold)
- ✅ Playwright + Chromium 설치됨
- ✅ `requirements.txt`에 playwright/fonttools/pytest-playwright 추가됨
- ✅ `design_tokens/duomo-detail.json` 존재 (액센트 파라미터화 완료)
- ✅ 렌더 파이프라인 스모크 검증 완료 (`demo_output/smoke/hero_smoke.png`)
- ✅ 재활용 모듈: `pipeline/copy.py`, `pipeline/library.py`, `pipeline/image_gen.py`, `storage/drive.py`, `auth/`

검증: `python -c "import playwright; from playwright.sync_api import sync_playwright; print('playwright ok')"` → `playwright ok`

---

## Task 1: 브랜드 액센트 맵

**Files:**
- Create: `design_tokens/brand_accents.json`
- Create: `tests/test_brand_accents.py`

- [ ] **Step 1: 실패하는 테스트 작성**

Create `tests/test_brand_accents.py`:
```python
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
    """골드는 어떤 브랜드 액센트로도 존재하면 안 된다."""
    data = json.loads(ACCENTS.read_text(encoding="utf-8"))
    assert GOLD == "#D4AF37"
    assert all(v.upper() != GOLD for v in data.values())
```

- [ ] **Step 2: 테스트 실패 확인**

Run: `python -m pytest tests/test_brand_accents.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'render'`

- [ ] **Step 3: 데이터 + 로더 구현**

Create `design_tokens/brand_accents.json`:
```json
{
  "Artemide": "#DE0515",
  "Knoll": "#DE0515",
  "Flos": "#29406C",
  "B&B Italia": "#1F1F1F",
  "Cassina": "#1F1F1F",
  "Marset": "#1F1F1F",
  "Santa&Cole": "#1F1F1F",
  "Vibia": "#1F1F1F",
  "Lasvit": "#1F1F1F",
  "Astep": "#1F1F1F",
  "Martinelli Luce": "#1F1F1F",
  "Flototto": "#1F1F1F",
  "_default": "#1F1F1F"
}
```

Create `render/__init__.py`:
```python
"""HTML/CSS 렌더링 패키지."""
```

Create `render/accents.py`:
```python
"""브랜드 액센트 컬러 해석. 골드는 절대 사용하지 않는다(Figma 전수조사 결론)."""
from __future__ import annotations

import json
from pathlib import Path

GOLD = "#D4AF37"
_PATH = Path(__file__).parent.parent / "design_tokens" / "brand_accents.json"
_MAP: dict[str, str] | None = None


def _load() -> dict[str, str]:
    global _MAP
    if _MAP is None:
        _MAP = json.loads(_PATH.read_text(encoding="utf-8"))
    return _MAP


def resolve_accent(brand: str) -> str:
    """브랜드명으로 액센트 hex를 반환한다. 미등록 브랜드는 _default."""
    m = _load()
    lower = {k.lower(): v for k, v in m.items()}
    return lower.get((brand or "").strip().lower(), m["_default"])
```

- [ ] **Step 4: 테스트 통과 확인**

Run: `python -m pytest tests/test_brand_accents.py -v`
Expected: 4 PASS

- [ ] **Step 5: 커밋**

```bash
git add design_tokens/brand_accents.json render/__init__.py render/accents.py tests/test_brand_accents.py
git commit -m "feat: brand accent map (no gold) + resolver"
```

---

## Task 2: 토큰 → CSS 변수

**Files:**
- Create: `render/css.py`
- Create: `tests/test_css.py`

- [ ] **Step 1: 실패하는 테스트 작성**

Create `tests/test_css.py`:
```python
"""토큰→CSS 변수 + @font-face 빌더 테스트."""
from pathlib import Path

from render.css import tokens_to_css_vars, font_face_block, base_css

PROJECT = Path(__file__).parent.parent
TOKENS = PROJECT / "design_tokens" / "premium-editorial.json"  # 기존 토큰 재활용 가능
FONTS = PROJECT / "fonts"


def _tokens():
    import json
    # duomo-detail.json 우선, 없으면 premium-editorial
    p = PROJECT / "design_tokens" / "duomo-detail.json"
    return json.loads(p.read_text(encoding="utf-8"))


def test_css_vars_include_accent_override():
    css = tokens_to_css_vars(_tokens(), accent="#29406C")
    assert "--accent: #29406C" in css
    assert "--w: 1000px" in css


def test_css_vars_use_white_background():
    css = tokens_to_css_vars(_tokens(), accent="#1F1F1F")
    assert "--bg: #FFFFFF" in css


def test_font_face_embeds_woff2_base64():
    block = font_face_block(FONTS)
    assert "@font-face" in block
    assert "Pretendard" in block
    assert "Serif" in block
    assert "base64," in block  # 인라인 임베드


def test_base_css_centers_and_locks_width():
    css = base_css()
    assert "text-align:center" in css.replace(" ", "")
    assert "1000px" in css
```

- [ ] **Step 2: 테스트 실패 확인**

Run: `python -m pytest tests/test_css.py -v`
Expected: FAIL — `cannot import name 'tokens_to_css_vars'`

- [ ] **Step 3: `render/css.py` 구현**

Create `render/css.py`:
```python
"""디자인 토큰과 폰트를 CSS로 변환한다. 폰트는 base64로 인라인(외부 의존 0)."""
from __future__ import annotations

import base64
from pathlib import Path
from typing import Any

# (CSS family name, woff2 파일명)
_FONTS = [
    ("Pretendard", "Pretendard-Regular.woff2"),
    ("PretendardM", "Pretendard-Medium.woff2"),
    ("PretendardSB", "Pretendard-SemiBold.woff2"),
    ("Serif", "NotoSerifDisplay-SemiBold.woff2"),
]


def font_face_block(fonts_dir: Path) -> str:
    """woff2를 base64로 인라인한 @font-face 블록."""
    out = []
    for family, fname in _FONTS:
        p = fonts_dir / fname
        b64 = base64.b64encode(p.read_bytes()).decode()
        out.append(
            f"@font-face{{font-family:'{family}';"
            f"src:url(data:font/woff2;base64,{b64}) format('woff2');"
            f"font-display:block;}}"
        )
    return "".join(out)


def tokens_to_css_vars(tokens: dict[str, Any], accent: str) -> str:
    """:root CSS 변수. accent는 브랜드별로 덮어쓴다."""
    c = tokens["color"]
    layout = tokens.get("layout", {})
    return (
        ":root{"
        f"--bg: {c.get('background', '#FFFFFF')};"
        f"--bg-dark: {c.get('background_alt', '#0A0A0A')};"
        f"--text: {c.get('text_primary', '#1F1F1F')};"
        f"--text-sub: {c.get('secondary', '#888888')};"
        f"--text-inv: {c.get('text_inverse', '#FFFFFF')};"
        f"--accent: {accent};"
        f"--divider: {c.get('divider', '#C4C4C4')};"
        f"--w: {layout.get('max_width', 1000)}px;"
        f"--pad-y: {layout.get('section_inner_padding_y', 160)}px;"
        f"--pad-x: {layout.get('outer_padding_x', 80)}px;"
        "}"
    )


def base_css() -> str:
    """모든 블록 공통 CSS (리셋·중앙정렬·1000px 락)."""
    return (
        "*{margin:0;padding:0;box-sizing:border-box;}"
        "body{width:1000px;background:var(--bg);}"
        ".block{width:1000px;text-align:center;}"
        ".block.dark{background:var(--bg-dark);color:var(--text-inv);}"
        ".block.light{background:var(--bg);color:var(--text);}"
        ".kr{font-family:Pretendard;}"
        ".kr-sb{font-family:PretendardSB;}"
        ".serif{font-family:Serif;font-weight:600;}"
        ".label{font-family:PretendardSB;font-size:14px;letter-spacing:8px;color:var(--accent);}"
        ".divider{width:60px;height:1px;background:var(--accent);margin:0 auto;}"
    )
```

- [ ] **Step 4: 테스트 통과 확인**

Run: `python -m pytest tests/test_css.py -v`
Expected: 4 PASS

- [ ] **Step 5: 커밋**

```bash
git add render/css.py tests/test_css.py
git commit -m "feat: tokens->CSS vars + base64 font-face + base CSS"
```

---

## Task 3: 블록 인터페이스 (base)

**Files:**
- Create: `blocks/__init__.py`
- Create: `blocks/base.py`
- Create: `tests/test_block_base.py`

- [ ] **Step 1: 실패하는 테스트 작성**

Create `tests/test_block_base.py`:
```python
"""블록 base 인터페이스 테스트."""
from blocks.base import BlockSpec, Field, escape_html


def test_field_construction():
    f = Field(key="statement", label="브랜드 철학", kind="textarea")
    assert f.key == "statement"
    assert f.kind == "textarea"


def test_blockspec_construction():
    spec = BlockSpec(
        type="brand", label="브랜드 스테이트먼트", category="U",
        input_fields=[Field("statement", "철학", "textarea")],
        copy_schema={"statement": "string"},
    )
    assert spec.type == "brand"
    assert spec.category == "U"
    assert spec.input_fields[0].key == "statement"


def test_escape_html_blocks_injection():
    assert escape_html("<script>") == "&lt;script&gt;"
    assert escape_html("B&B") == "B&amp;B"
    assert escape_html("a\"b") == "a&quot;b"


def test_escape_html_handles_none():
    assert escape_html(None) == ""
```

- [ ] **Step 2: 테스트 실패 확인**

Run: `python -m pytest tests/test_block_base.py -v`
Expected: FAIL — `No module named 'blocks'`

- [ ] **Step 3: `blocks/base.py` 구현**

Create `blocks/__init__.py`:
```python
"""쇼케이스 블록 패키지."""
```

Create `blocks/base.py`:
```python
"""블록 공통 인터페이스. 각 블록은 spec(메타)과 render(data,tokens,refs)->HTML을 가진다."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable


@dataclass
class Field:
    """UI 입력 필드 정의."""
    key: str
    label: str
    kind: str  # "text" | "textarea" | "list" | "image"


@dataclass
class BlockSpec:
    """블록 메타데이터."""
    type: str           # "brand" | "designer" | "hero" | ...
    label: str          # UI 표시명
    category: str       # "U" | "O" | "F" | "L"
    input_fields: list[Field] = field(default_factory=list)
    copy_schema: dict[str, Any] = field(default_factory=dict)


@runtime_checkable
class Block(Protocol):
    """블록 프로토콜."""
    spec: BlockSpec

    def render(self, data: dict[str, Any], tokens: dict[str, Any],
               refs: dict[str, str]) -> str:
        """HTML 조각(<section>...)을 반환한다."""
        ...


_ESCAPE = {"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"}


def escape_html(text: Any) -> str:
    """HTML 특수문자 이스케이프. None은 빈 문자열."""
    if text is None:
        return ""
    s = str(text)
    return "".join(_ESCAPE.get(ch, ch) for ch in s)


def nl2br(text: Any) -> str:
    """줄바꿈을 <br>로. 먼저 이스케이프."""
    return escape_html(text).replace("\n", "<br>")
```

- [ ] **Step 4: 테스트 통과 확인**

Run: `python -m pytest tests/test_block_base.py -v`
Expected: 4 PASS

- [ ] **Step 5: 커밋**

```bash
git add blocks/__init__.py blocks/base.py tests/test_block_base.py
git commit -m "feat: block base interface (BlockSpec, Field, html escaping)"
```

---

## Task 4: hero 블록

**Files:**
- Create: `blocks/hero.py`
- Create: `tests/test_block_hero.py`

- [ ] **Step 1: 실패하는 테스트 작성**

Create `tests/test_block_hero.py`:
```python
"""hero 블록 렌더 테스트."""
from blocks.hero import HeroBlock


def test_hero_spec():
    b = HeroBlock()
    assert b.spec.type == "hero"
    assert b.spec.category == "U"


def test_hero_renders_serif_product_name_and_korean_sub():
    b = HeroBlock()
    html = b.render(
        data={"product_en": "Camaleonda", "variant": "Fabric",
              "subhead": "은은한 빛이 따뜻한", "ref": "bg"},
        tokens={}, refs={"bg": "data:image/png;base64,AAA"},
    )
    assert "<section" in html and "hero" in html
    assert "Camaleonda" in html
    assert "은은한 빛이 따뜻한" in html
    assert "serif" in html              # 제품명은 serif 클래스
    assert "data:image/png;base64,AAA" in html  # 배경 인라인


def test_hero_escapes_text():
    b = HeroBlock()
    html = b.render({"product_en": "A&B", "subhead": "<x>", "ref": "bg"},
                    {}, {"bg": "u"})
    assert "A&amp;B" in html
    assert "&lt;x&gt;" in html


def test_hero_no_background_uses_placeholder():
    b = HeroBlock()
    html = b.render({"product_en": "X", "subhead": "y"}, {}, {})
    assert "<section" in html  # 깨지지 않음
```

- [ ] **Step 2: 테스트 실패 확인**

Run: `python -m pytest tests/test_block_hero.py -v`
Expected: FAIL — `No module named 'blocks.hero'`

- [ ] **Step 3: `blocks/hero.py` 구현**

Create `blocks/hero.py`:
```python
"""Hero 블록 — 풀블리드 배경 + 다크 오버레이 + 중앙 하단 텍스트(한글 서브→세리프 제품명)."""
from __future__ import annotations

from typing import Any

from blocks.base import BlockSpec, Field, escape_html

_CSS = (
    "<style>"
    ".hero{position:relative;height:1200px;background-size:cover;background-position:center;}"
    ".hero .ov{position:absolute;inset:0;background:rgba(10,10,10,.55);}"
    ".hero .ht{position:absolute;bottom:140px;left:0;right:0;color:#fff;}"
    ".hero .sub{font-size:40px;letter-spacing:-.8px;margin-bottom:24px;}"
    ".hero h1{font-size:106px;line-height:1;}"
    ".hero h2{font-size:80px;line-height:1;margin-top:12px;}"
    "</style>"
)


class HeroBlock:
    spec = BlockSpec(
        type="hero", label="히어로 (제품명)", category="U",
        input_fields=[
            Field("product_en", "제품명(영문)", "text"),
            Field("variant", "변형명", "text"),
            Field("subhead", "한글 서브카피", "text"),
            Field("ref", "배경 이미지", "image"),
        ],
        copy_schema={"product_en": "string", "variant": "string", "subhead": "string"},
    )

    def render(self, data: dict[str, Any], tokens: dict[str, Any],
               refs: dict[str, str]) -> str:
        bg = refs.get(data.get("ref", ""), "")
        style = f"background-image:url('{bg}');" if bg else "background:#9a9a9a;"
        variant = data.get("variant")
        v_html = f'<h2 class="serif">{escape_html(variant)}</h2>' if variant else ""
        return (
            _CSS +
            f'<section class="block hero" style="{style}">'
            '<div class="ov"></div>'
            '<div class="ht">'
            f'<div class="sub kr">{escape_html(data.get("subhead"))}</div>'
            f'<h1 class="serif">{escape_html(data.get("product_en"))}</h1>'
            f'{v_html}'
            '</div></section>'
        )
```

- [ ] **Step 4: 테스트 통과 확인**

Run: `python -m pytest tests/test_block_hero.py -v`
Expected: 4 PASS

- [ ] **Step 5: 커밋**

```bash
git add blocks/hero.py tests/test_block_hero.py
git commit -m "feat: hero block (full-bleed bg + dark overlay + serif name)"
```

---

## Task 5: brand · designer 블록

**Files:**
- Create: `blocks/brand.py`
- Create: `blocks/designer.py`
- Create: `tests/test_block_brand_designer.py`

- [ ] **Step 1: 실패하는 테스트 작성**

Create `tests/test_block_brand_designer.py`:
```python
"""brand / designer 블록 테스트."""
from blocks.brand import BrandBlock
from blocks.designer import DesignerBlock


def test_brand_renders_label_and_statement():
    b = BrandBlock()
    html = b.render({"brand": "B&B Italia", "statement": "1966년 브리아자",
                     "dark": False}, {}, {})
    assert "B&amp;B Italia" in html          # label 이스케이프
    assert "1966" in html
    assert "label" in html                   # 골드 아닌 var(--accent) 라벨
    assert "light" in html                   # dark=False → light


def test_brand_dark_mode():
    b = BrandBlock()
    html = b.render({"brand": "Flos", "statement": "s", "dark": True}, {}, {})
    assert "dark" in html


def test_designer_renders_name_bio_portrait():
    d = DesignerBlock()
    html = d.render({"name": "Mario Bellini", "bio": "MoMA 영구 소장",
                     "ref": "p", "dark": True}, {}, {"p": "data:img"})
    assert "Mario Bellini" in html
    assert "MoMA" in html
    assert "DESIGNER" in html                 # 영문 라벨
    assert "data:img" in html                 # 인물 사진 인라인


def test_designer_without_portrait_ok():
    d = DesignerBlock()
    html = d.render({"name": "X", "bio": "y"}, {}, {})
    assert "<section" in html
```

- [ ] **Step 2: 테스트 실패 확인**

Run: `python -m pytest tests/test_block_brand_designer.py -v`
Expected: FAIL — `No module named 'blocks.brand'`

- [ ] **Step 3: 구현**

Create `blocks/brand.py`:
```python
"""Brand statement 블록 — 라벨(브랜드명, accent색) + 경어체 철학 문장. 다크/라이트."""
from __future__ import annotations

from typing import Any

from blocks.base import BlockSpec, Field, escape_html, nl2br

_CSS = (
    "<style>"
    ".brand{padding:var(--pad-y) var(--pad-x);}"
    ".brand .label{margin-bottom:44px;}"
    ".brand p{font-size:40px;line-height:1.44;letter-spacing:-.8px;}"
    "</style>"
)


class BrandBlock:
    spec = BlockSpec(
        type="brand", label="브랜드 스테이트먼트", category="U",
        input_fields=[
            Field("brand", "브랜드명", "text"),
            Field("statement", "브랜드 철학(경어체)", "textarea"),
            Field("dark", "다크 배경", "text"),
        ],
        copy_schema={"statement": "string"},
    )

    def render(self, data: dict[str, Any], tokens: dict[str, Any],
               refs: dict[str, str]) -> str:
        mode = "dark" if data.get("dark") else "light"
        return (
            _CSS +
            f'<section class="block brand {mode}">'
            f'<div class="label">{escape_html(data.get("brand")).upper()}</div>'
            f'<p class="kr-sb">{nl2br(data.get("statement"))}</p>'
            '</section>'
        )
```

Create `blocks/designer.py`:
```python
"""Designer 블록 — 'DESIGNER' 라벨 + 이름 + 바이오 + 인물 사진. 보통 다크 배경."""
from __future__ import annotations

from typing import Any

from blocks.base import BlockSpec, Field, escape_html, nl2br

_CSS = (
    "<style>"
    ".designer{padding:var(--pad-y) var(--pad-x);}"
    ".designer .portrait{width:360px;height:440px;object-fit:cover;"
    "margin:0 auto 48px;display:block;}"
    ".designer .role{font-family:PretendardSB;font-size:14px;letter-spacing:8px;"
    "color:var(--accent);margin-bottom:20px;}"
    ".designer h3{font-family:Serif;font-size:48px;margin-bottom:28px;}"
    ".designer p{font-size:24px;line-height:1.6;}"
    "</style>"
)


class DesignerBlock:
    spec = BlockSpec(
        type="designer", label="디자이너", category="U",
        input_fields=[
            Field("name", "디자이너명", "text"),
            Field("bio", "바이오(경어체)", "textarea"),
            Field("ref", "인물 사진", "image"),
            Field("dark", "다크 배경", "text"),
        ],
        copy_schema={"bio": "string"},
    )

    def render(self, data: dict[str, Any], tokens: dict[str, Any],
               refs: dict[str, str]) -> str:
        mode = "dark" if data.get("dark", True) else "light"
        portrait = refs.get(data.get("ref", ""), "")
        img = f'<img class="portrait" src="{portrait}">' if portrait else ""
        return (
            _CSS +
            f'<section class="block designer {mode}">'
            f'{img}'
            '<div class="role">DESIGNER</div>'
            f'<h3>{escape_html(data.get("name"))}</h3>'
            f'<p class="kr">{nl2br(data.get("bio"))}</p>'
            '</section>'
        )
```

- [ ] **Step 4: 테스트 통과 확인**

Run: `python -m pytest tests/test_block_brand_designer.py -v`
Expected: 4 PASS

- [ ] **Step 5: 커밋**

```bash
git add blocks/brand.py blocks/designer.py tests/test_block_brand_designer.py
git commit -m "feat: brand + designer blocks"
```

---

## Task 6: intro · lifestyle · closing 블록

**Files:**
- Create: `blocks/intro.py`
- Create: `blocks/lifestyle.py`
- Create: `blocks/closing.py`
- Create: `tests/test_block_intro_lifestyle_closing.py`

- [ ] **Step 1: 실패하는 테스트 작성**

Create `tests/test_block_intro_lifestyle_closing.py`:
```python
"""intro / lifestyle / closing 블록 테스트."""
from blocks.intro import IntroBlock
from blocks.lifestyle import LifestyleBlock
from blocks.closing import ClosingBlock


def test_intro_centered_body():
    html = IntroBlock().render({"body": "둥근 형태의 소파입니다"}, {}, {})
    assert "둥근 형태의 소파입니다" in html
    assert "intro" in html


def test_lifestyle_fullbleed_image():
    html = LifestyleBlock().render({"caption": "거실", "ref": "img"}, {},
                                   {"img": "data:bg"})
    assert "data:bg" in html
    assert "거실" in html


def test_lifestyle_caption_optional():
    html = LifestyleBlock().render({"ref": "img"}, {}, {"img": "data:bg"})
    assert "<section" in html


def test_closing_soft_cta_no_hardsell():
    html = ClosingBlock().render({"text": "추가 옵션은 채널톡으로 문의해주세요"}, {}, {})
    assert "채널톡" in html
    assert "closing" in html
```

- [ ] **Step 2: 테스트 실패 확인**

Run: `python -m pytest tests/test_block_intro_lifestyle_closing.py -v`
Expected: FAIL — `No module named 'blocks.intro'`

- [ ] **Step 3: 구현**

Create `blocks/intro.py`:
```python
"""제품 소개 문단 — 흰 배경, 중앙, 경어체 본문."""
from __future__ import annotations

from typing import Any

from blocks.base import BlockSpec, Field, nl2br

_CSS = ("<style>.intro{padding:var(--pad-y) var(--pad-x);}"
        ".intro p{font-size:40px;line-height:1.44;letter-spacing:-.8px;color:var(--text);}"
        "</style>")


class IntroBlock:
    spec = BlockSpec(
        type="intro", label="제품 소개", category="U",
        input_fields=[Field("body", "소개 문단(경어체)", "textarea")],
        copy_schema={"body": "string"},
    )

    def render(self, data: dict[str, Any], tokens: dict[str, Any],
               refs: dict[str, str]) -> str:
        return (_CSS + '<section class="block intro light">'
                f'<p class="kr-sb">{nl2br(data.get("body"))}</p></section>')
```

Create `blocks/lifestyle.py`:
```python
"""라이프스타일 — 풀블리드 인테리어 사진 + (선택) 캡션."""
from __future__ import annotations

from typing import Any

from blocks.base import BlockSpec, Field, escape_html

_CSS = ("<style>.lifestyle img{width:1000px;display:block;}"
        ".lifestyle .cap{padding:40px var(--pad-x);font-family:Pretendard;"
        "font-size:24px;color:var(--text-sub);}"
        ".lifestyle .ph{width:1000px;height:700px;background:#cfcabf;}"
        "</style>")


class LifestyleBlock:
    spec = BlockSpec(
        type="lifestyle", label="라이프스타일 사진", category="U",
        input_fields=[
            Field("ref", "사진", "image"),
            Field("caption", "캡션(선택)", "text"),
        ],
        copy_schema={"caption": "string"},
    )

    def render(self, data: dict[str, Any], tokens: dict[str, Any],
               refs: dict[str, str]) -> str:
        img_src = refs.get(data.get("ref", ""), "")
        img = (f'<img src="{img_src}">' if img_src
               else '<div class="ph"></div>')
        cap = data.get("caption")
        cap_html = f'<div class="cap">{escape_html(cap)}</div>' if cap else ""
        return (_CSS + '<section class="block lifestyle light">'
                f'{img}{cap_html}</section>')
```

Create `blocks/closing.py`:
```python
"""마무리 문의 — 소프트 CTA(채널톡 안내). 하드셀/가격/긴급성 금지."""
from __future__ import annotations

from typing import Any

from blocks.base import BlockSpec, Field, nl2br

_CSS = ("<style>.closing{padding:var(--pad-y) var(--pad-x);}"
        ".closing p{font-size:32px;line-height:1.5;color:var(--text-inv);}"
        "</style>")


class ClosingBlock:
    spec = BlockSpec(
        type="closing", label="마무리 문의", category="U",
        input_fields=[Field("text", "문의 안내(소프트)", "textarea")],
        copy_schema={"text": "string"},
    )

    def render(self, data: dict[str, Any], tokens: dict[str, Any],
               refs: dict[str, str]) -> str:
        return (_CSS + '<section class="block closing dark">'
                f'<p class="kr">{nl2br(data.get("text"))}</p></section>')
```

- [ ] **Step 4: 테스트 통과 확인**

Run: `python -m pytest tests/test_block_intro_lifestyle_closing.py -v`
Expected: 4 PASS

- [ ] **Step 5: 커밋**

```bash
git add blocks/intro.py blocks/lifestyle.py blocks/closing.py tests/test_block_intro_lifestyle_closing.py
git commit -m "feat: intro + lifestyle + closing blocks"
```

---

## Task 7: 블록 레지스트리

**Files:**
- Create: `blocks/registry.py`
- Create: `tests/test_registry.py`

- [ ] **Step 1: 실패하는 테스트 작성**

Create `tests/test_registry.py`:
```python
"""블록 레지스트리 테스트."""
import pytest

from blocks.registry import get_block, list_blocks, BlockNotFound


def test_core_blocks_registered():
    types = {b.type for b in list_blocks()}
    assert {"hero", "brand", "designer", "intro", "lifestyle", "closing"} <= types


def test_get_block_returns_instance():
    b = get_block("hero")
    assert b.spec.type == "hero"
    assert hasattr(b, "render")


def test_unknown_block_raises():
    with pytest.raises(BlockNotFound):
        get_block("nonexistent")


def test_list_blocks_have_categories():
    for b in list_blocks():
        assert b.category in ("U", "O", "F", "L")
```

- [ ] **Step 2: 테스트 실패 확인**

Run: `python -m pytest tests/test_registry.py -v`
Expected: FAIL — `No module named 'blocks.registry'`

- [ ] **Step 3: `blocks/registry.py` 구현**

Create `blocks/registry.py`:
```python
"""블록 타입 → 블록 인스턴스 레지스트리."""
from __future__ import annotations

from blocks.base import Block, BlockSpec
from blocks.brand import BrandBlock
from blocks.closing import ClosingBlock
from blocks.designer import DesignerBlock
from blocks.hero import HeroBlock
from blocks.intro import IntroBlock
from blocks.lifestyle import LifestyleBlock


class BlockNotFound(Exception):
    """등록되지 않은 블록 타입."""


_REGISTRY: dict[str, Block] = {}


def _register(block: Block) -> None:
    _REGISTRY[block.spec.type] = block


for _b in (HeroBlock(), BrandBlock(), DesignerBlock(),
           IntroBlock(), LifestyleBlock(), ClosingBlock()):
    _register(_b)


def get_block(block_type: str) -> Block:
    """타입으로 블록 인스턴스를 반환한다."""
    if block_type not in _REGISTRY:
        raise BlockNotFound(f"Unknown block type: {block_type}")
    return _REGISTRY[block_type]


def list_blocks() -> list[BlockSpec]:
    """등록된 모든 블록의 spec 리스트."""
    return [b.spec for b in _REGISTRY.values()]
```

- [ ] **Step 4: 테스트 통과 확인**

Run: `python -m pytest tests/test_registry.py -v`
Expected: 4 PASS

- [ ] **Step 5: 커밋**

```bash
git add blocks/registry.py tests/test_registry.py
git commit -m "feat: block registry"
```

---

## Task 8: 페이지 빌더 (recipe → HTML)

**Files:**
- Create: `render/page_builder.py`
- Create: `tests/test_page_builder.py`

- [ ] **Step 1: 실패하는 테스트 작성**

Create `tests/test_page_builder.py`:
```python
"""레시피 → 완성 HTML 빌더 테스트."""
from pathlib import Path

from render.page_builder import build_page

FONTS = Path(__file__).parent.parent / "fonts"


def _recipe():
    return {
        "meta": {"brand": "B&B Italia", "accent": "#1F1F1F"},
        "blocks": [
            {"type": "brand", "data": {"brand": "B&B Italia",
                                       "statement": "1966년", "dark": True}},
            {"type": "intro", "data": {"body": "소개 문단"}},
            {"type": "closing", "data": {"text": "채널톡 문의"}},
        ],
    }


def test_build_page_returns_full_html():
    html = build_page(_recipe(), fonts_dir=FONTS)
    assert html.lstrip().startswith("<!doctype html")
    assert "@font-face" in html
    assert "--accent: #1F1F1F" in html


def test_build_page_preserves_block_order():
    html = build_page(_recipe(), fonts_dir=FONTS)
    i_brand = html.index("1966년")
    i_intro = html.index("소개 문단")
    i_closing = html.index("채널톡 문의")
    assert i_brand < i_intro < i_closing


def test_build_page_skips_unknown_block_gracefully():
    recipe = {"meta": {"brand": "X", "accent": "#1F1F1F"},
              "blocks": [{"type": "nonexistent", "data": {}},
                         {"type": "intro", "data": {"body": "ok"}}]}
    html = build_page(recipe, fonts_dir=FONTS)
    assert "ok" in html  # 알 수 없는 블록은 건너뛰고 진행


def test_build_page_defaults_accent_from_brand_when_missing():
    recipe = {"meta": {"brand": "Artemide"},
              "blocks": [{"type": "intro", "data": {"body": "x"}}]}
    html = build_page(recipe, fonts_dir=FONTS)
    assert "--accent: #DE0515" in html  # 브랜드 액센트 맵에서 해석
```

- [ ] **Step 2: 테스트 실패 확인**

Run: `python -m pytest tests/test_page_builder.py -v`
Expected: FAIL — `cannot import name 'build_page'`

- [ ] **Step 3: `render/page_builder.py` 구현**

Create `render/page_builder.py`:
```python
"""레시피(블록 리스트) → 완성 1000px HTML 문서."""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from blocks.registry import BlockNotFound, get_block
from render.accents import resolve_accent
from render.css import base_css, font_face_block, tokens_to_css_vars

log = logging.getLogger(__name__)

_TOKENS_PATH = Path(__file__).parent.parent / "design_tokens" / "duomo-detail.json"


def _load_tokens() -> dict[str, Any]:
    return json.loads(_TOKENS_PATH.read_text(encoding="utf-8"))


def build_page(recipe: dict[str, Any], fonts_dir: Path,
               refs: dict[str, str] | None = None) -> str:
    """레시피를 완성 HTML로 빌드한다.

    accent 우선순위: meta.accent > 브랜드 액센트 맵 > _default.
    알 수 없는 블록 타입은 로그 경고 후 건너뛴다.
    """
    refs = refs or {}
    meta = recipe.get("meta", {})
    accent = meta.get("accent") or resolve_accent(meta.get("brand", ""))
    tokens = _load_tokens()

    head = (
        "<!doctype html><html><head><meta charset='utf-8'><style>"
        + font_face_block(fonts_dir)
        + tokens_to_css_vars(tokens, accent)
        + base_css()
        + "</style></head><body>"
    )

    body_parts: list[str] = []
    for entry in recipe.get("blocks", []):
        btype = entry.get("type", "")
        try:
            block = get_block(btype)
        except BlockNotFound:
            log.warning("skipping unknown block: %s", btype)
            continue
        body_parts.append(block.render(entry.get("data", {}), tokens, refs))

    return head + "".join(body_parts) + "</body></html>"
```

- [ ] **Step 4: 테스트 통과 확인**

Run: `python -m pytest tests/test_page_builder.py -v`
Expected: 4 PASS

- [ ] **Step 5: 커밋**

```bash
git add render/page_builder.py tests/test_page_builder.py
git commit -m "feat: page builder (recipe -> 1000px HTML, accent resolution)"
```

---

## Task 9: Playwright 렌더러

**Files:**
- Create: `render/renderer.py`
- Create: `tests/test_renderer.py`

- [ ] **Step 1: 실패하는 테스트 작성**

Create `tests/test_renderer.py`:
```python
"""Playwright 렌더러 통합 테스트 (실제 Chromium 사용)."""
from pathlib import Path

from PIL import Image

from render.page_builder import build_page
from render.renderer import render_html_to_png

FONTS = Path(__file__).parent.parent / "fonts"


def test_render_produces_1000px_png(tmp_path):
    recipe = {
        "meta": {"brand": "B&B Italia", "accent": "#1F1F1F"},
        "blocks": [
            {"type": "brand", "data": {"brand": "B&B Italia",
                                       "statement": "1966년 브리아자", "dark": True}},
            {"type": "intro", "data": {"body": "둥근 형태의 소파입니다"}},
        ],
    }
    html = build_page(recipe, fonts_dir=FONTS)
    out = tmp_path / "page.png"
    render_html_to_png(html, out)
    assert out.exists()
    img = Image.open(out)
    assert img.width == 1000
    assert img.height > 300  # 두 섹션 쌓임
```

- [ ] **Step 2: 테스트 실패 확인**

Run: `python -m pytest tests/test_renderer.py -v`
Expected: FAIL — `cannot import name 'render_html_to_png'`

- [ ] **Step 3: `render/renderer.py` 구현**

Create `render/renderer.py`:
```python
"""HTML → 1000px full_page PNG (Playwright 헤드리스 Chromium)."""
from __future__ import annotations

from pathlib import Path

from playwright.sync_api import sync_playwright


class RenderError(Exception):
    """렌더 실패."""


def render_html_to_png(html: str, out_path: Path, width: int = 1000) -> Path:
    """HTML 문자열을 width px 폭의 full_page PNG로 캡처한다.

    Raises:
        RenderError: Chromium 미설치 등 렌더 실패
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": width, "height": 1400})
            page.set_content(html, wait_until="networkidle")
            page.screenshot(path=str(out_path), full_page=True, type="png")
            browser.close()
    except Exception as e:  # noqa: BLE001 — 외부 브라우저 경로 다양
        raise RenderError(
            f"렌더 실패: {e}. Chromium 설치 필요 시 'python -m playwright install chromium'"
        ) from e
    return out_path
```

- [ ] **Step 4: 테스트 통과 확인**

Run: `python -m pytest tests/test_renderer.py -v`
Expected: 1 PASS (Chromium 사용, ~5초)

- [ ] **Step 5: 커밋**

```bash
git add render/renderer.py tests/test_renderer.py
git commit -m "feat: Playwright renderer (HTML -> 1000px full_page PNG)"
```

---

## Task 10: color_options · dimension 블록

**Files:**
- Create: `blocks/color_options.py`
- Create: `blocks/dimension.py`
- Modify: `blocks/registry.py`
- Create: `tests/test_block_color_dimension.py`

- [ ] **Step 1: 실패하는 테스트 작성**

Create `tests/test_block_color_dimension.py`:
```python
"""color_options / dimension 블록 테스트."""
from blocks.color_options import ColorOptionsBlock
from blocks.dimension import DimensionBlock
from blocks.registry import get_block


def test_color_options_renders_swatch_grid():
    html = ColorOptionsBlock().render(
        {"label": "패브릭",
         "swatches": [{"name": "Enia 103", "hex": "#8B7E6E"},
                      {"name": "Enia 111", "hex": "#3D4A3A"}]},
        {}, {})
    assert "패브릭" in html
    assert "Enia 103" in html
    assert "#8B7E6E" in html
    assert "swatch" in html


def test_color_options_empty_swatches_ok():
    html = ColorOptionsBlock().render({"label": "색상", "swatches": []}, {}, {})
    assert "<section" in html


def test_dimension_renders_values_and_drawing():
    html = DimensionBlock().render(
        {"values": "W288×D96×H67×SH55", "ref": "d"}, {}, {"d": "data:img"})
    assert "W288" in html
    assert "data:img" in html
    assert "DIMENSION" in html


def test_color_and_dimension_in_registry():
    assert get_block("color_options").spec.type == "color_options"
    assert get_block("dimension").spec.type == "dimension"
```

- [ ] **Step 2: 테스트 실패 확인**

Run: `python -m pytest tests/test_block_color_dimension.py -v`
Expected: FAIL — `No module named 'blocks.color_options'`

- [ ] **Step 3: 구현 + 레지스트리 등록**

Create `blocks/color_options.py`:
```python
"""색상/마감 옵션 — 라벨 + 원형 스와치 그리드 (가구=패브릭/조명=마감)."""
from __future__ import annotations

from typing import Any

from blocks.base import BlockSpec, Field, escape_html

_CSS = (
    "<style>"
    ".coloropt{padding:var(--pad-y) var(--pad-x);}"
    ".coloropt h4{font-family:PretendardSB;font-size:40px;margin-bottom:48px;}"
    ".coloropt .grid{display:flex;flex-wrap:wrap;justify-content:center;gap:32px;}"
    ".coloropt .swatch{width:160px;}"
    ".coloropt .dot{width:80px;height:80px;border-radius:50%;"
    "border:1px solid var(--divider);margin:0 auto 16px;}"
    ".coloropt .nm{font-family:PretendardM;font-size:24px;color:var(--text);}"
    "</style>"
)


class ColorOptionsBlock:
    spec = BlockSpec(
        type="color_options", label="색상/마감 옵션", category="U",
        input_fields=[
            Field("label", "라벨(예: 색상/패브릭)", "text"),
            Field("swatches", "스와치 [{name,hex}]", "list"),
        ],
        copy_schema={"label": "string"},
    )

    def render(self, data: dict[str, Any], tokens: dict[str, Any],
               refs: dict[str, str]) -> str:
        cells = []
        for sw in data.get("swatches", []):
            hexv = escape_html(sw.get("hex", "#CCCCCC"))
            cells.append(
                '<div class="swatch">'
                f'<div class="dot" style="background:{hexv};"></div>'
                f'<div class="nm">{escape_html(sw.get("name"))}</div></div>'
            )
        return (
            _CSS + '<section class="block coloropt light">'
            f'<h4>{escape_html(data.get("label"))}</h4>'
            f'<div class="grid">{"".join(cells)}</div></section>'
        )
```

Create `blocks/dimension.py`:
```python
"""치수 — 'DIMENSION' 라벨 + 값(W×D×H×SH) + (선택) 라인 도면 이미지."""
from __future__ import annotations

from typing import Any

from blocks.base import BlockSpec, Field, escape_html

_CSS = (
    "<style>"
    ".dim{padding:var(--pad-y) var(--pad-x);}"
    ".dim .role{font-family:PretendardSB;font-size:14px;letter-spacing:8px;"
    "color:var(--accent);margin-bottom:32px;}"
    ".dim img{max-width:700px;display:block;margin:0 auto 32px;}"
    ".dim .val{font-family:PretendardM;font-size:28px;color:var(--text);}"
    "</style>"
)


class DimensionBlock:
    spec = BlockSpec(
        type="dimension", label="치수", category="O",
        input_fields=[
            Field("values", "치수값(예: W288×D96×H67×SH55)", "text"),
            Field("ref", "도면 이미지(선택)", "image"),
        ],
        copy_schema={},
    )

    def render(self, data: dict[str, Any], tokens: dict[str, Any],
               refs: dict[str, str]) -> str:
        drawing = refs.get(data.get("ref", ""), "")
        img = f'<img src="{drawing}">' if drawing else ""
        return (
            _CSS + '<section class="block dim light">'
            '<div class="role">DIMENSION</div>'
            f'{img}<div class="val">{escape_html(data.get("values"))}</div>'
            '</section>'
        )
```

Modify `blocks/registry.py` — imports와 등록 루프에 추가:
```python
from blocks.color_options import ColorOptionsBlock
from blocks.dimension import DimensionBlock
```
그리고 등록 루프를 다음으로 교체:
```python
for _b in (HeroBlock(), BrandBlock(), DesignerBlock(),
           IntroBlock(), LifestyleBlock(), ClosingBlock(),
           ColorOptionsBlock(), DimensionBlock()):
    _register(_b)
```

- [ ] **Step 4: 테스트 통과 확인**

Run: `python -m pytest tests/test_block_color_dimension.py -v`
Expected: 4 PASS

- [ ] **Step 5: 커밋**

```bash
git add blocks/color_options.py blocks/dimension.py blocks/registry.py tests/test_block_color_dimension.py
git commit -m "feat: color_options + dimension blocks"
```

---

## Task 11: trust_block · spec_table · material 블록

**Files:**
- Create: `blocks/trust_block.py`
- Create: `blocks/spec_table.py`
- Create: `blocks/material.py`
- Modify: `blocks/registry.py`
- Create: `tests/test_block_trust_spec_material.py`

- [ ] **Step 1: 실패하는 테스트 작성**

Create `tests/test_block_trust_spec_material.py`:
```python
"""trust_block / spec_table / material 블록 테스트."""
from blocks.trust_block import TrustBlock
from blocks.spec_table import SpecTableBlock
from blocks.material import MaterialBlock
from blocks.registry import get_block


def test_trust_block_renders_importer_and_benefits():
    html = TrustBlock().render(
        {"importer": "DUOMO&Co. 한국 공식 수입사",
         "benefits": ["무료배송", "5년 A/S", "KC인증"]}, {}, {})
    assert "공식 수입사" in html
    assert "무료배송" in html
    assert "KC인증" in html


def test_spec_table_renders_rows():
    html = SpecTableBlock().render(
        {"rows": [["품명", "Camaleonda"], ["소재", "Fabric"],
                  ["KC인증", "ZW11055-22008"]]}, {}, {})
    assert "품명" in html
    assert "Camaleonda" in html
    assert "ZW11055-22008" in html


def test_material_renders_text_and_macro():
    html = MaterialBlock().render(
        {"title": "소재", "body": "투명 크리스탈", "ref": "m"}, {}, {"m": "data:img"})
    assert "투명 크리스탈" in html
    assert "data:img" in html


def test_all_three_in_registry():
    for t in ("trust_block", "spec_table", "material"):
        assert get_block(t).spec.type == t
```

- [ ] **Step 2: 테스트 실패 확인**

Run: `python -m pytest tests/test_block_trust_spec_material.py -v`
Expected: FAIL — `No module named 'blocks.trust_block'`

- [ ] **Step 3: 구현 + 레지스트리 등록**

Create `blocks/trust_block.py`:
```python
"""공식 수입사 신뢰 블록 — 수입사 명 + 혜택 셀 그리드 (무료배송·교환·A/S·KC 등)."""
from __future__ import annotations

from typing import Any

from blocks.base import BlockSpec, Field, escape_html

_CSS = (
    "<style>"
    ".trust{padding:var(--pad-y) var(--pad-x);}"
    ".trust .imp{font-family:Serif;font-size:36px;margin-bottom:48px;}"
    ".trust .cells{display:flex;flex-wrap:wrap;justify-content:center;gap:24px;}"
    ".trust .cell{min-width:260px;padding:28px 0;border:1px solid var(--divider);"
    "font-family:PretendardM;font-size:26px;color:var(--text);}"
    "</style>"
)


class TrustBlock:
    spec = BlockSpec(
        type="trust_block", label="공식 수입사 신뢰블록", category="O",
        input_fields=[
            Field("importer", "수입사 명", "text"),
            Field("benefits", "혜택 리스트", "list"),
        ],
        copy_schema={},
    )

    def render(self, data: dict[str, Any], tokens: dict[str, Any],
               refs: dict[str, str]) -> str:
        cells = "".join(
            f'<div class="cell">{escape_html(b)}</div>'
            for b in data.get("benefits", [])
        )
        return (
            _CSS + '<section class="block trust light">'
            f'<div class="imp">{escape_html(data.get("importer"))}</div>'
            f'<div class="cells">{cells}</div></section>'
        )
```

Create `blocks/spec_table.py`:
```python
"""상품정보 스펙표 — 라벨/값 2열 행 리스트."""
from __future__ import annotations

from typing import Any

from blocks.base import BlockSpec, Field, escape_html

_CSS = (
    "<style>"
    ".spec{padding:var(--pad-y) var(--pad-x);}"
    ".spec table{width:100%;border-collapse:collapse;font-family:Pretendard;}"
    ".spec td{padding:20px 8px;border-bottom:1px solid var(--divider);font-size:24px;}"
    ".spec td.k{text-align:left;color:var(--text-sub);width:30%;}"
    ".spec td.v{text-align:left;color:var(--text);}"
    "</style>"
)


class SpecTableBlock:
    spec = BlockSpec(
        type="spec_table", label="상품정보 스펙표", category="O",
        input_fields=[Field("rows", "행 [[라벨,값],...]", "list")],
        copy_schema={},
    )

    def render(self, data: dict[str, Any], tokens: dict[str, Any],
               refs: dict[str, str]) -> str:
        rows = "".join(
            f'<tr><td class="k">{escape_html(r[0])}</td>'
            f'<td class="v">{escape_html(r[1])}</td></tr>'
            for r in data.get("rows", []) if len(r) >= 2
        )
        return (_CSS + '<section class="block spec light">'
                f'<table>{rows}</table></section>')
```

Create `blocks/material.py`:
```python
"""소재/특징 — 제목 + 본문 + 매크로 사진."""
from __future__ import annotations

from typing import Any

from blocks.base import BlockSpec, Field, escape_html, nl2br

_CSS = (
    "<style>"
    ".material{padding:var(--pad-y) var(--pad-x);}"
    ".material h4{font-family:PretendardSB;font-size:40px;margin-bottom:32px;}"
    ".material p{font-family:Pretendard;font-size:28px;line-height:1.6;"
    "color:var(--text);margin-bottom:48px;}"
    ".material img{width:1000px;display:block;margin-left:calc(-1*var(--pad-x));}"
    "</style>"
)


class MaterialBlock:
    spec = BlockSpec(
        type="material", label="소재/특징", category="O",
        input_fields=[
            Field("title", "제목", "text"),
            Field("body", "설명(경어체)", "textarea"),
            Field("ref", "매크로 사진", "image"),
        ],
        copy_schema={"title": "string", "body": "string"},
    )

    def render(self, data: dict[str, Any], tokens: dict[str, Any],
               refs: dict[str, str]) -> str:
        macro = refs.get(data.get("ref", ""), "")
        img = f'<img src="{macro}">' if macro else ""
        return (
            _CSS + '<section class="block material light">'
            f'<h4>{escape_html(data.get("title"))}</h4>'
            f'<p>{nl2br(data.get("body"))}</p>{img}</section>'
        )
```

Modify `blocks/registry.py` — imports 추가:
```python
from blocks.trust_block import TrustBlock
from blocks.spec_table import SpecTableBlock
from blocks.material import MaterialBlock
```
등록 루프 교체:
```python
for _b in (HeroBlock(), BrandBlock(), DesignerBlock(),
           IntroBlock(), LifestyleBlock(), ClosingBlock(),
           ColorOptionsBlock(), DimensionBlock(),
           TrustBlock(), SpecTableBlock(), MaterialBlock()):
    _register(_b)
```

- [ ] **Step 4: 테스트 통과 확인**

Run: `python -m pytest tests/test_block_trust_spec_material.py -v`
Expected: 4 PASS

- [ ] **Step 5: 커밋**

```bash
git add blocks/trust_block.py blocks/spec_table.py blocks/material.py blocks/registry.py tests/test_block_trust_spec_material.py
git commit -m "feat: trust_block + spec_table + material blocks"
```

---

## Task 12: 쇼케이스 카피 생성

**Files:**
- Create: `prompts/showcase-copy.md`
- Modify: `pipeline/copy.py` (append)
- Create: `tests/test_showcase_copy.py`

- [ ] **Step 1: 실패하는 테스트 작성**

Create `tests/test_showcase_copy.py`:
```python
"""블록 단위 쇼케이스 카피 생성 테스트 (모킹)."""
import json
from unittest.mock import MagicMock

from pipeline.copy import generate_block_copy, CopyError


def _mock(text):
    m = MagicMock()
    m.content = [MagicMock(text=text)]
    return m


def test_generate_block_copy_returns_dict(tmp_path):
    fake = json.dumps({"statement": "1966년 브리아자에서 시작되었습니다"},
                      ensure_ascii=False)
    client = MagicMock()
    client.messages.create.return_value = _mock(fake)
    prompt = tmp_path / "showcase-copy.md"
    prompt.write_text("system", encoding="utf-8")

    out = generate_block_copy(
        client=client, block_type="brand",
        copy_schema={"statement": "string"},
        meta={"brand": "B&B Italia"},
        system_prompt_path=prompt,
    )
    assert out["statement"].startswith("1966")


def test_generate_block_copy_retries_on_bad_json(tmp_path):
    bad = _mock("음 그러니까")
    good = _mock(json.dumps({"body": "둥근 소파입니다"}, ensure_ascii=False))
    client = MagicMock()
    client.messages.create.side_effect = [bad, good]
    prompt = tmp_path / "p.md"; prompt.write_text("s", encoding="utf-8")

    out = generate_block_copy(
        client=client, block_type="intro",
        copy_schema={"body": "string"}, meta={},
        system_prompt_path=prompt,
    )
    assert out["body"].startswith("둥근")
    assert client.messages.create.call_count == 2
```

- [ ] **Step 2: 테스트 실패 확인**

Run: `python -m pytest tests/test_showcase_copy.py -v`
Expected: FAIL — `cannot import name 'generate_block_copy'`

- [ ] **Step 3: 프롬프트 + 함수 구현**

Create `prompts/showcase-copy.md`:
```markdown
# DUOMO 쇼케이스 카피 (블록 단위)

너는 DUOMO(유럽 프리미엄 가구·조명 정식 수입사)의 상세페이지 카피라이터다.
요청된 블록 하나의 카피만 JSON으로 생성한다.

## 절대 규칙 (Figma 전수조사 12브랜드/26제품 기반)
- **판매 퍼널 금지**: Pain/Problem/공포/긴급성/가격/할인/한정/"지금 구매" 류 일절 금지
- **제품 쇼케이스 톤**: 브랜드 헤리티지·디자이너 스토리·소재/구조 서사
- **경어체** (~합니다/~입니다/~됩니다). 번역투·유행어·밈 금지
- **CTA는 소프트만**: "채널톡으로 문의해주세요" 수준. 하드셀 금지
- 감성과 정보를 한 문장에 엮는다(분리하지 않음)
- 출력은 **JSON만**, 다른 텍스트 없이

## 블록별 가이드
- brand: 브랜드의 설립·철학을 2~3줄 경어체로. 예) "1966년 브리아자에서 시작된 …는 …을 만들어왔습니다."
- designer: 디자이너의 이력·대표작·수상을 담백하게. 과장 금지
- hero: subhead는 제품의 감각을 한 줄로(제품명·변형명은 입력값 유지)
- intro: 제품의 형태·용도·자리를 짧은 경어체 문단으로
- material: 소재/구조의 특징을 정보+감각으로
- color_options: 라벨만(예: "색상"/"패브릭")
- closing: 추가 옵션·문의를 소프트하게 안내

요청은 다음 형식으로 온다: 블록타입, copy_schema(채울 키), meta(브랜드·제품·디자이너).
copy_schema의 키를 모두 채운 JSON을 반환하라.
```

Append to `pipeline/copy.py`:
```python
def generate_block_copy(
    *,
    client,
    block_type: str,
    copy_schema: dict,
    meta: dict,
    system_prompt_path: Path,
    model: str = "claude-sonnet-4-5",
    max_tokens: int = 2000,
) -> dict:
    """쇼케이스 블록 하나의 카피를 생성한다. JSON 파싱 실패 시 1회 재시도.

    Raises:
        CopyError: 2회 시도 후에도 JSON 파싱 실패
    """
    system = system_prompt_path.read_text(encoding="utf-8")
    user = (
        f"블록타입: {block_type}\n"
        f"copy_schema: {json.dumps(copy_schema, ensure_ascii=False)}\n"
        f"meta: {json.dumps(meta, ensure_ascii=False)}\n\n"
        "copy_schema의 키를 모두 채운 JSON만 출력하라."
    )
    return _call_with_retry(
        client=client, system_prompt=system, user_msg=user,
        model=model, max_tokens=max_tokens, label=f"block:{block_type}",
    )
```

(주의: `_call_with_retry`, `json`, `Path`는 기존 `pipeline/copy.py`에 이미 존재. 추가 import 불필요.)

- [ ] **Step 4: 테스트 통과 확인**

Run: `python -m pytest tests/test_showcase_copy.py -v`
Expected: 2 PASS

- [ ] **Step 5: 커밋**

```bash
git add prompts/showcase-copy.md pipeline/copy.py tests/test_showcase_copy.py
git commit -m "feat: block-level showcase copy generation (no funnel)"
```

---

## Task 13: 레거시 정리 + 통합 E2E 검증

**Files:**
- Create: `tests/test_e2e_showcase.py`
- Create: `prompts/_funnel/` (기존 funnel 카피 이동)

- [ ] **Step 1: funnel 카피 보존 이동**

Run (PowerShell):
```powershell
New-Item -ItemType Directory -Force -Path "prompts/_funnel" | Out-Null
Copy-Item "prompts/03-copy.md" "prompts/_funnel/03-copy.md"
```
(원본은 남겨둠 — 기존 pipeline/copy.py가 참조하므로 삭제하지 않음. _funnel은 비-DUOMO 프리셋 참조용 보존 사본.)

- [ ] **Step 2: E2E 테스트 작성 (실제 렌더)**

Create `tests/test_e2e_showcase.py`:
```python
"""전체 파이프라인 E2E: 레시피 → HTML → PNG (실제 Chromium)."""
from pathlib import Path

from PIL import Image

from render.page_builder import build_page
from render.renderer import render_html_to_png

FONTS = Path(__file__).parent.parent / "fonts"


def test_full_showcase_recipe_renders(tmp_path):
    """B&B Camaleonda 풀 레시피가 1000px 세로 PNG로 렌더된다."""
    recipe = {
        "meta": {"brand": "B&B Italia", "product": "Camaleonda",
                 "designer": "Mario Bellini", "category": "furniture",
                 "accent": "#1F1F1F"},
        "blocks": [
            {"type": "brand", "data": {"brand": "B&B Italia",
             "statement": "1966년 브리아자에서 시작되었습니다", "dark": True}},
            {"type": "designer", "data": {"name": "Mario Bellini",
             "bio": "MoMA 영구 소장 디자이너입니다", "dark": True}},
            {"type": "hero", "data": {"product_en": "Camaleonda",
             "variant": "Fabric", "subhead": "모듈로 완성하는 공간"}},
            {"type": "intro", "data": {"body": "둥근 모듈로 자유롭게 구성합니다"}},
            {"type": "color_options", "data": {"label": "패브릭",
             "swatches": [{"name": "Enia 103", "hex": "#8B7E6E"},
                          {"name": "Enia 111", "hex": "#3D4A3A"}]}},
            {"type": "dimension", "data": {"values": "W288×D96×H67×SH55"}},
            {"type": "closing", "data": {"text": "추가 구성은 채널톡으로 문의해주세요"}},
        ],
    }
    html = build_page(recipe, fonts_dir=FONTS)
    out = tmp_path / "camaleonda.png"
    render_html_to_png(html, out)

    img = Image.open(out)
    assert img.width == 1000
    assert img.height > 2000  # 7개 섹션
    # 첫 행은 다크(brand), 흰 영역도 존재하는지 대략 확인
    px_top = img.getpixel((500, 50))
    assert sum(px_top[:3]) < 200  # 상단 brand 다크
```

- [ ] **Step 3: E2E 통과 확인**

Run: `python -m pytest tests/test_e2e_showcase.py -v`
Expected: 1 PASS (~5초)

- [ ] **Step 4: 전체 테스트 통과 확인**

Run: `python -m pytest tests/ -q`
Expected: 모든 테스트 PASS (기존 + 신규 블록/렌더/카피 ~40+개)

- [ ] **Step 5: 커밋**

```bash
git add tests/test_e2e_showcase.py prompts/_funnel/
git commit -m "test: E2E showcase pipeline + preserve funnel copy"
```

---

## Task 14: Streamlit UI — 메타 + 블록 조립

**Files:**
- Modify: `pages/1_new_project.py` (전면 재작성)
- Create: `pipeline/recipe.py` (세션→레시피 헬퍼)
- Create: `tests/test_recipe.py`

- [ ] **Step 1: recipe 헬퍼 테스트 작성**

Create `tests/test_recipe.py`:
```python
"""레시피 조작 헬퍼 테스트."""
from pipeline.recipe import new_recipe, add_block, remove_block, move_block


def test_new_recipe_has_meta_and_empty_blocks():
    r = new_recipe(brand="B&B Italia", product="Camaleonda")
    assert r["meta"]["brand"] == "B&B Italia"
    assert r["blocks"] == []


def test_add_block_appends():
    r = new_recipe(brand="X")
    add_block(r, "hero")
    assert r["blocks"][0]["type"] == "hero"
    assert r["blocks"][0]["data"] == {}


def test_remove_block_by_index():
    r = new_recipe(brand="X")
    add_block(r, "hero"); add_block(r, "intro")
    remove_block(r, 0)
    assert len(r["blocks"]) == 1
    assert r["blocks"][0]["type"] == "intro"


def test_move_block_up():
    r = new_recipe(brand="X")
    add_block(r, "hero"); add_block(r, "intro")
    move_block(r, 1, -1)  # intro를 위로
    assert r["blocks"][0]["type"] == "intro"


def test_move_block_bounds_safe():
    r = new_recipe(brand="X")
    add_block(r, "hero")
    move_block(r, 0, -1)  # 맨 위에서 위로 — 변화 없음
    assert r["blocks"][0]["type"] == "hero"
```

- [ ] **Step 2: 테스트 실패 확인**

Run: `python -m pytest tests/test_recipe.py -v`
Expected: FAIL — `No module named 'pipeline.recipe'`

- [ ] **Step 3: `pipeline/recipe.py` 구현**

Create `pipeline/recipe.py`:
```python
"""레시피(블록 리스트) 조작 헬퍼 — UI 세션 상태에서 사용."""
from __future__ import annotations

from typing import Any


def new_recipe(*, brand: str = "", product: str = "", designer: str = "",
               category: str = "furniture", accent: str = "") -> dict[str, Any]:
    """빈 레시피를 만든다."""
    return {
        "meta": {"brand": brand, "product": product, "designer": designer,
                 "category": category, "accent": accent},
        "blocks": [],
    }


def add_block(recipe: dict[str, Any], block_type: str) -> None:
    """블록을 맨 끝에 추가한다."""
    recipe["blocks"].append({"type": block_type, "data": {}})


def remove_block(recipe: dict[str, Any], index: int) -> None:
    """index 블록을 제거한다."""
    if 0 <= index < len(recipe["blocks"]):
        recipe["blocks"].pop(index)


def move_block(recipe: dict[str, Any], index: int, delta: int) -> None:
    """블록을 delta만큼 이동한다(-1 위 / +1 아래). 범위 밖이면 무시."""
    blocks = recipe["blocks"]
    new_idx = index + delta
    if 0 <= index < len(blocks) and 0 <= new_idx < len(blocks):
        blocks[index], blocks[new_idx] = blocks[new_idx], blocks[index]
```

- [ ] **Step 4: 테스트 통과 확인**

Run: `python -m pytest tests/test_recipe.py -v`
Expected: 5 PASS

- [ ] **Step 5: `pages/1_new_project.py` 재작성 (UI Step 1~2)**

Replace entire `pages/1_new_project.py`:
```python
"""신규 프로젝트 — 쇼케이스 블록 조립 위저드."""
from __future__ import annotations

import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from blocks.registry import list_blocks
from pipeline.recipe import new_recipe, add_block, remove_block, move_block
from render.accents import resolve_accent

load_dotenv()

if not st.session_state.get("user_email"):
    st.error("먼저 로그인하세요.")
    st.stop()

st.title("신규 상세페이지")

if "recipe" not in st.session_state:
    st.session_state.recipe = None
if "wizard_step" not in st.session_state:
    st.session_state.wizard_step = 1


def _step1_meta():
    st.header("1단계 · 기본 정보")
    with st.form("meta"):
        col1, col2 = st.columns(2)
        with col1:
            brand = st.text_input("브랜드", placeholder="B&B Italia")
            product = st.text_input("제품명", placeholder="Camaleonda")
        with col2:
            designer = st.text_input("디자이너", placeholder="Mario Bellini")
            category = st.selectbox("카테고리", ["furniture", "lighting"])
        if st.form_submit_button("다음: 블록 조립", type="primary"):
            if not brand:
                st.error("브랜드는 필수입니다.")
                return
            accent = resolve_accent(brand)
            st.session_state.recipe = new_recipe(
                brand=brand, product=product, designer=designer,
                category=category, accent=accent)
            st.session_state.wizard_step = 2
            st.rerun()
    st.caption("브랜드를 입력하면 액센트 컬러가 자동 적용됩니다 (골드 없음).")


def _step2_compose():
    r = st.session_state.recipe
    st.header("2단계 · 블록 조립")
    st.caption(f"브랜드: {r['meta']['brand']} · 액센트: {r['meta']['accent']}")

    # 블록 팔레트
    specs = {s.label: s.type for s in list_blocks()}
    cat_hint = ("가구: brand·designer·hero·intro·material·color_options·dimension·closing 권장"
                if r["meta"]["category"] == "furniture"
                else "조명: brand·designer·hero·intro·color_options·spec_table·dimension·closing 권장")
    st.info(cat_hint)
    pick = st.selectbox("블록 추가", list(specs.keys()))
    if st.button("+ 추가"):
        add_block(r, specs[pick])
        st.rerun()

    st.markdown("---")
    # 현재 레시피 (순서/삭제)
    if not r["blocks"]:
        st.write("아직 블록이 없습니다. 위에서 추가하세요.")
    for i, blk in enumerate(r["blocks"]):
        c1, c2, c3, c4 = st.columns([5, 1, 1, 1])
        with c1:
            st.write(f"**{i+1}. {blk['type']}**")
        with c2:
            if st.button("↑", key=f"up{i}"):
                move_block(r, i, -1); st.rerun()
        with c3:
            if st.button("↓", key=f"dn{i}"):
                move_block(r, i, +1); st.rerun()
        with c4:
            if st.button("✕", key=f"rm{i}"):
                remove_block(r, i); st.rerun()

    st.markdown("---")
    cols = st.columns(2)
    with cols[0]:
        if st.button("← 기본 정보"):
            st.session_state.wizard_step = 1; st.rerun()
    with cols[1]:
        if st.button("다음: 데이터 입력 →", type="primary", disabled=not r["blocks"]):
            st.session_state.wizard_step = 3; st.rerun()


def _step3_placeholder():
    st.header("3단계 · 데이터 입력 & 렌더")
    st.info("Task 15에서 구현 — 블록별 카피/이미지 입력 + 렌더")
    if st.button("← 블록 조립"):
        st.session_state.wizard_step = 2; st.rerun()


step = st.session_state.wizard_step
if step == 1 or st.session_state.recipe is None:
    _step1_meta()
elif step == 2:
    _step2_compose()
else:
    _step3_placeholder()
```

- [ ] **Step 6: 문법 확인**

Run: `python -m py_compile pages/1_new_project.py pipeline/recipe.py`
Expected: 에러 없음

- [ ] **Step 7: 커밋**

```bash
git add pages/1_new_project.py pipeline/recipe.py tests/test_recipe.py
git commit -m "feat: showcase wizard step 1-2 (meta + block composition)"
```

---

## Task 15: Streamlit UI — 데이터 입력 + 렌더 (Step 3)

**Files:**
- Modify: `pages/1_new_project.py` (Step 3 구현)

- [ ] **Step 1: Step 3 구현**

`pages/1_new_project.py`에서 `_step3_placeholder()` 함수를 다음으로 교체:
```python
import anthropic
from blocks.registry import get_block
from render.page_builder import build_page
from render.renderer import render_html_to_png
from pipeline.copy import generate_block_copy, CopyError

PROJECT = Path(__file__).parent.parent
FONTS = PROJECT / "fonts"
PROMPTS = PROJECT / "prompts"


@st.cache_resource
def _claude():
    return anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def _collect_refs(r) -> dict:
    """업로드/생성된 이미지를 base64 data-uri로 모은다."""
    import base64
    refs = {}
    for i, blk in enumerate(r["blocks"]):
        ref_key = blk["data"].get("ref")
        upload = st.session_state.get(f"img_{i}")
        if ref_key and upload is not None:
            b64 = base64.b64encode(upload).decode()
            refs[ref_key] = f"data:image/jpeg;base64,{b64}"
    return refs


def _step3_data():
    r = st.session_state.recipe
    st.header("3단계 · 데이터 입력 & 렌더")

    for i, blk in enumerate(r["blocks"]):
        spec = get_block(blk["type"]).spec
        with st.expander(f"{i+1}. {spec.label} ({blk['type']})", expanded=False):
            # 카피 자동생성 버튼 (copy_schema 있는 블록만)
            if spec.copy_schema and st.button("✨ 카피 생성", key=f"gen{i}"):
                try:
                    out = generate_block_copy(
                        client=_claude(), block_type=blk["type"],
                        copy_schema=spec.copy_schema, meta=r["meta"],
                        system_prompt_path=PROMPTS / "showcase-copy.md")
                    blk["data"].update(out)
                    st.rerun()
                except CopyError as e:
                    st.error(f"카피 생성 실패: {e}")
            # 입력 필드
            for f in spec.input_fields:
                cur = blk["data"].get(f.key, "")
                if f.kind == "textarea":
                    blk["data"][f.key] = st.text_area(
                        f.label, value=cur, key=f"f_{i}_{f.key}")
                elif f.kind == "image":
                    up = st.file_uploader(f.label, type=["jpg", "jpeg", "png"],
                                          key=f"up_{i}_{f.key}")
                    if up is not None:
                        st.session_state[f"img_{i}"] = up.read()
                        blk["data"][f.key] = f"ref_{i}"
                elif f.kind == "list":
                    st.caption(f"{f.label} — JSON으로 입력")
                    raw = st.text_area(f.label, value=str(cur or "[]"),
                                       key=f"l_{i}_{f.key}")
                    try:
                        import json as _j
                        blk["data"][f.key] = _j.loads(raw)
                    except Exception:
                        st.warning("리스트 JSON 형식 오류")
                else:
                    blk["data"][f.key] = st.text_input(
                        f.label, value=cur, key=f"f_{i}_{f.key}")

    st.markdown("---")
    if st.button("🎨 상세페이지 렌더", type="primary"):
        refs = _collect_refs(r)
        html = build_page(r, fonts_dir=FONTS, refs=refs)
        out_dir = Path("/tmp/duomo-showcase") / st.session_state["user_email"]
        out_dir.mkdir(parents=True, exist_ok=True)
        out = out_dir / "page.png"
        with st.spinner("렌더링 중..."):
            render_html_to_png(html, out)
        st.session_state.rendered_path = str(out)
        st.rerun()

    if st.session_state.get("rendered_path"):
        st.image(st.session_state.rendered_path, use_container_width=True)
        with open(st.session_state.rendered_path, "rb") as fh:
            st.download_button("📥 PNG 다운로드", data=fh,
                               file_name=f"{r['meta'].get('product','duomo')}.png",
                               mime="image/png")

    if st.button("← 블록 조립"):
        st.session_state.wizard_step = 2; st.rerun()
```

그리고 라우팅의 `else: _step3_placeholder()`를 `else: _step3_data()`로 교체.

- [ ] **Step 2: 문법 확인**

Run: `python -m py_compile pages/1_new_project.py`
Expected: 에러 없음

- [ ] **Step 3: 로컬 수동 검증 (DEMO_MODE)**

`.env`에 `DEMO_MODE=1`, `ANTHROPIC_API_KEY`, fonts 준비된 상태에서:
Run: `streamlit run app.py`
브라우저에서: 1단계(B&B Italia 입력) → 2단계(brand·hero·intro·closing 추가, 순서 조정) → 3단계(카피 생성 + 렌더) → PNG 미리보기·다운로드 확인.

- [ ] **Step 4: 커밋**

```bash
git add pages/1_new_project.py
git commit -m "feat: showcase wizard step 3 (data input + copy gen + render)"
```

---

## Task 16: deprecated 표시 + README

**Files:**
- Modify: `pipeline/compose.py` (상단 deprecation 주석)
- Modify: `pipeline/stitch.py` (상단 deprecation 주석)
- Modify: `README.md`

- [ ] **Step 1: deprecation 주석 추가**

`pipeline/compose.py` 최상단에 추가:
```python
"""[DEPRECATED] PIL 합성 — 쇼케이스 재설계(blocks/ + render/)로 대체됨.
비-DUOMO 퍼널 프리셋 참조용으로만 보존. 신규 작업은 render/page_builder.py 사용."""
```

`pipeline/stitch.py` 최상단에 동일 패턴으로:
```python
"""[DEPRECATED] PIL 세로 스티칭 — Playwright full_page 캡처로 대체됨.
보존용. 신규 작업은 render/renderer.py 사용."""
```

- [ ] **Step 2: README 갱신**

`README.md`의 실행 섹션에 추가:
```markdown
## 쇼케이스 생성기 (신규)

DUOMO Figma 톤(1000px·중앙·순백·브랜드컬러·쇼케이스)의 HTML/CSS 블록 생성기.

```bash
pip install -r requirements.txt
python -m playwright install chromium   # 최초 1회
streamlit run app.py
```

흐름: 기본정보(브랜드→액센트 자동) → 블록 조립(추가/순서/삭제) → 블록별 카피·이미지 → 렌더 → PNG.

블록: hero·brand·designer·intro·lifestyle·material·color_options·dimension·spec_table·trust_block·closing.
구조/톤 근거: docs/playbook/visual-tone.md (Figma 전수조사 12브랜드/26제품).
```

- [ ] **Step 3: 전체 테스트 최종 확인**

Run: `python -m pytest tests/ -q`
Expected: 모든 테스트 PASS

- [ ] **Step 4: 커밋**

```bash
git add pipeline/compose.py pipeline/stitch.py README.md
git commit -m "docs: deprecate PIL pipeline, document showcase generator"
```

---

## 완료 기준

- [ ] 11종 블록 전부 구현 + 레지스트리 등록
- [ ] 토큰→CSS, 브랜드 액센트(골드 없음), 폰트 인라인
- [ ] page_builder: 레시피→HTML, 블록 순서 보존, 미지 블록 graceful skip
- [ ] Playwright 렌더: HTML→1000px full_page PNG
- [ ] 쇼케이스 카피 생성 (퍼널 금지)
- [ ] Streamlit 위저드: 메타→조립(추가/순서/삭제)→데이터→렌더→다운로드
- [ ] E2E: B&B Camaleonda 풀 레시피 렌더 성공
- [ ] 전체 테스트 green (기존 + 신규 ~50개)
- [ ] PIL 파이프라인 deprecated 표시 (삭제 아닌 보존)
