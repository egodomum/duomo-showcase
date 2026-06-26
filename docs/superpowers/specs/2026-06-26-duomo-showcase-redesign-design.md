# DUOMO Showcase 재설계 — Design Spec

- **작성일**: 2026-06-26
- **상태**: Draft (사용자 검토 대기)
- **선행**: Figma 전수조사(12브랜드/26제품) → [visual-tone.md](../../playbook/visual-tone.md), [duomo-detail.json](../../../design_tokens/duomo-detail.json)
- **대체 대상**: 기존 13섹션 퍼널 도구 ([2026-05-26 design](2026-05-26-duomo-landing-tool-design.md))

---

## 1. 배경 & 문제

기존 도구는 13섹션 **판매 퍼널**(Pain→Problem→…→Final CTA), 1200px, 좌측정렬, 골드 액센트, PIL 합성으로 만들어졌다. 그러나 Figma 전수조사 결과 **DUOMO 실제 상세페이지는 정반대**다:

- **제품 쇼케이스** 구조 — 12브랜드/26제품 전부에서 Pain/Problem/CTA/가격/긴급성 **0개**
- **1000px · 중앙정렬 · 순백배경 · 브랜드컬러 액센트(골드 절대 없음)**
- 척추: 브랜드 스테이트먼트 → 디자이너 → 라이프스타일
- 정교한 섹션(스와치 그리드·패브릭 비교표·CAD 치수도면·믹스드 세리프/산세)

→ 기존 도구는 **수정이 아니라 재설계** 대상. 본 스펙은 쇼케이스 생성기로 전면 재구축한다.

## 2. 목표 / 비목표

### 목표
- DUOMO Figma 톤을 충실히 재현하는 상세페이지 자동 생성
- **완전 자유 섹션 조립** — 사용자가 블록을 추가/삭제/순서변경
- 가구·조명 양 카테고리 + 2세대(구/리뉴얼) 지원
- 브랜드별 액센트 자동 적용 (골드 금지)
- 1000px 세로 PNG 출력 (카페24/29CM/SSG 호환)

### 비목표 (V2)
- 드래그앤드롭(MVP는 ↑↓ 버튼)
- 2세대 자동 판별(수동 선택)
- 채널별 750px 변형
- CAD 치수 자동 작도(이미지 업로드로 대체)
- 비교표 고급 인라인 편집

## 3. 핵심 결정 (Decision Log)

| 결정 | 대안 | 이유 |
|---|---|---|
| **HTML/CSS + Playwright 렌더** | PIL 확장 / Figma 직접 | 쇼케이스가 PIL로 재현 불가 수준으로 정교(스와치·비교표·CAD·에디토리얼). CSS면 충실+자유조립 자연스러움 |
| **블록 레지스트리** | 고정 템플릿 2종 | 완전 자유 조립 요구. Figma 실제가 재사용 컴포넌트(가이드/section) 방식 |
| **전체 1회 캡처** | 블록별 캡처+스티칭 | 단순. HTML이라 섹션 데이터 편집 후 전체 재렌더가 싸다 |
| **funnel 카피 보존** | 삭제 | 비-DUOMO 고객용 별도 프리셋으로 유지 |

## 4. 아키텍처

```
[Streamlit UI] 블록 팔레트 조립 + 데이터 입력
   ▼ recipe.json (순서있는 블록 리스트)
[block registry] blocks/*.py — 블록타입별 render(data,tokens,refs)→HTML조각
   ▼
[page builder] render/page_builder.py — 블록 HTML들을 1000px 컨테이너로 결합
   ▼
[renderer] render/renderer.py — Playwright 헤드리스 → 1000px full_page PNG
   ▼
[output] 최종 PNG → 다운로드 + Drive 업로드
```

배경 이미지 소스(룩북/Gemini/업로드)는 기존 모듈 재활용, base64로 HTML 인라인.

## 5. 블록 인터페이스

```python
# blocks/base.py
@dataclass
class Field:
    key: str; label: str; kind: str  # "text"|"textarea"|"list"|"image"

@dataclass
class BlockSpec:
    type: str            # "brand"|"designer"|"hero"|...
    label: str           # UI 표시명
    category: str        # "U"|"O"|"F"|"L"
    input_fields: list[Field]
    copy_schema: dict    # Claude가 채울 구조

class Block(Protocol):
    spec: BlockSpec
    def render(self, data: dict, tokens: dict, refs: dict) -> str: ...  # HTML 조각
```

## 6. 블록 카탈로그 (MVP ~10종)

| 블록 type | cat | 입력 | 비고 |
|---|---|---|---|
| `trust_block` | O/L | 수입사·혜택 리스트(4~6셀) | 공식수입사 신뢰블록 |
| `brand` | U | 브랜드명·철학 카피·다크여부 | |
| `designer` | U | 이름·바이오·인물사진 | |
| `hero` | U | 제품명(EN)·변형·서브카피·배경 | 풀블리드+다크오버레이 |
| `intro` | U | 소개 문단 | |
| `lifestyle` | U | 사진·캡션 | 반복 추가 가능 |
| `material` | O | 소재 설명·매크로 사진 | |
| `color_options` | U | 스와치 그리드(가구=패브릭/조명=마감) | |
| `dimension` | O | 치수값·도면 이미지 | |
| `spec_table` | O | 상품정보(품명·KC·전압·소켓) | |
| `closing` | U | 마무리 문의(소프트 CTA) | 채널톡 |

가구 전용 추가(F): `module_system`, `comparison_table` — MVP 후순위 가능.

## 7. recipe.json 데이터 모델

```json
{
  "meta": {
    "brand": "B&B Italia", "product": "Camaleonda", "designer": "Mario Bellini",
    "category": "furniture", "generation": "renewal", "accent": "#1F1F1F"
  },
  "blocks": [
    { "type": "trust_block", "data": { "importer": "...", "benefits": ["...","..."] } },
    { "type": "brand",       "data": { "statement": "...", "dark": true } },
    { "type": "designer",    "data": { "name": "Mario Bellini", "bio": "...", "ref": "p.jpg" } },
    { "type": "hero",        "data": { "product_en": "Camaleonda", "subhead": "...", "ref": "h.jpg" } },
    { "type": "intro",       "data": { "body": "..." } },
    { "type": "lifestyle",   "data": { "caption": "...", "ref": "l1.jpg" } },
    { "type": "color_options","data": { "label": "패브릭", "swatches": [{"name":"Enia 103","hex":"#..."}] } },
    { "type": "dimension",   "data": { "values": "W288×D96×H67×SH55", "ref": "d.jpg" } },
    { "type": "closing",     "data": { "text": "..." } }
  ]
}
```

## 8. 토큰 → CSS

```python
# render/css.py
def tokens_to_css(tokens, accent) -> str  # :root CSS 변수 생성
# --bg #FFFFFF, --bg-dark #0A0A0A, --text #1F1F1F, --text-sub #888,
# --accent <브랜드>, --divider #C4C4C4, --w 1000px, --pad-y 160px, --pad-x 80px
```

폰트 @font-face(woff2): Pretendard-Regular/SemiBold(한글 본문), NotoSerifDisplay-SemiBold(영문 워드마크/제품명). 한글 제품명은 Figma가 라틴에만 세리프 적용하므로 문제 없음.

## 9. 브랜드 액센트 맵

```json
// design_tokens/brand_accents.json (전수조사 결과)
{ "Artemide":"#DE0515", "Knoll":"#DE0515", "Flos":"#29406C",
  "B&B Italia":"#1F1F1F", "Cassina":"#1F1F1F", "_default":"#1F1F1F" }
```
골드(#D4AF37)는 어떤 경우에도 액센트로 사용 금지.

## 10. 카피 생성

- 신규 `prompts/showcase-copy.md` — 플레이북 기반. 브랜드 헤리티지·디자이너 스토리·소재 서사, 경어체. **Pain/Problem/CTA/가격/긴급성/할인 금지**, 소프트 채널톡 문의만.
- 블록 단위로 `generate_block_copy(client, block_type, meta)` 호출, 블록의 `copy_schema`를 채움.
- 기존 funnel 카피(`03-copy.md` 등)는 `prompts/_funnel/`로 이동 보존.
- ⚠️ 데이터위생: 파이프라인은 노드명이 아닌 렌더 콘텐츠 기준(Figma 조사 시 노드명↔콘텐츠 불일치 만연했음). 생성기엔 직접 영향 없으나 룩북 인덱스 작성 시 유의.

## 11. UI (Streamlit 재구성)

`pages/1_new_project.py` 재작성:
1. **메타 입력** — 브랜드·제품·디자이너·카테고리(가구/조명)·세대 → 브랜드 선택 시 액센트 자동
2. **블록 조립** — 팔레트에서 추가, ↑↓로 순서, 삭제. 카테고리별 추천(가구→module/fabric, 조명→spec/dimension)
3. **블록별 데이터** — 카피(Claude 생성+편집) + 이미지(룩북/Gemini/업로드)
4. **렌더 미리보기** → 전체 PNG 다운로드 + Drive

블록 순서·데이터는 `st.session_state.recipe`로 관리.

## 12. 디렉터리 변화

```
blocks/                  신규: base.py + brand/designer/hero/intro/lifestyle/
                              material/color_options/dimension/spec_table/trust_block/closing.py
render/                  신규: css.py · page_builder.py · renderer.py(Playwright)
prompts/showcase-copy.md 신규
prompts/_funnel/         기존 funnel 카피 보존(03-copy.md 등 이동)
design_tokens/duomo-detail.json · brand_accents.json(신규)
fonts/*.woff2            Pretendard-Regular/SemiBold · NotoSerifDisplay 추가
pipeline/compose.py · stitch.py     → deprecated (블록/render로 대체, 삭제 아닌 보존)
pipeline/copy.py · library.py · image_gen.py · storage/drive.py · auth/  → 재활용
requirements.txt         playwright 추가
```

## 13. 에러 핸들링

| 실패 | 처리 |
|---|---|
| Playwright 미설치/브라우저 없음 | 명확한 안내 + `playwright install chromium` 가이드 |
| 블록 HTML 렌더 실패 | 해당 블록만 에러 표시, 나머지 진행 |
| 폰트 woff2 누락 | 시스템 폰트 폴백 + 경고 |
| 배경 이미지 없음(이미지 블록) | placeholder 회색 + 경고 |
| 브랜드 액센트 맵에 없는 브랜드 | `_default`(#1F1F1F) |
| Claude 카피 실패 | 빈 카피로 블록 생성, 수동 편집 유도 |

## 14. 테스트

```
blocks/test_blocks.py     각 블록 render()가 유효 HTML 조각 반환(스냅샷)
render/test_css.py        토큰→CSS 변수 매핑
render/test_page_builder.py  레시피→완성 HTML, 블록 순서 보존
render/test_renderer.py   Playwright로 샘플 레시피→1000px PNG(통합)
pipeline/test_copy.py     쇼케이스 카피 JSON 파싱(모킹)
```

## 15. 구현 단계 (plan에서 상세화)

1. 폰트 확보(woff2) + 토큰·액센트맵 + CSS 변환
2. 블록 base + 핵심 블록(brand·designer·hero·intro·lifestyle·closing)
3. page_builder + Playwright renderer + 통합 테스트
4. 나머지 블록(color_options·dimension·spec_table·trust_block·material)
5. 쇼케이스 카피 프롬프트 + copy.py 블록 연동
6. Streamlit UI 재구성(메타→조립→데이터→렌더)
7. 샘플(B&B Camaleonda·Artemide Onfale)로 E2E 검증

## 16. 완료 기준

- B&B Camaleonda·Artemide Onfale를 실제 Figma와 시각적으로 근접하게 재현
- 사용자가 블록 추가/삭제/순서변경 가능
- 브랜드 액센트 자동, 골드 없음
- 1000px 세로 PNG 출력 + Drive
- 전체 테스트 green

---

## 다음 단계
1. 사용자(Paul) 스펙 검토 → 승인
2. `superpowers:writing-plans`로 구현 계획 (새 세션 권장 — 메모리에 기록됨)
