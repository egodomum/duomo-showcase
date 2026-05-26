# DUOMO Landing Tool — Design Spec

- **작성일**: 2026-05-26
- **상태**: Draft (사용자 검토 대기)
- **작성자**: Paul + Claude (brainstorming 세션)
- **선행 자산**: [`~/.claude/skills/landing-page-generator/`](../../../../../.claude/skills/landing-page-generator/) (DUOMO 톤 재작성된 카피·디자인·프롬프트 가이드)

---

## 1. 개요

DUOMO 내부 5~15명이 카페24/폐쇄몰용 상세페이지 이미지를 빠르게 만들기 위한 사내 웹 도구. 정식 수입 본사 룩북 사진을 라이브러리로 관리하고, Claude로 13섹션 카피를 생성한 뒤, PIL로 이미지+타이포를 합성해 1200px 너비의 긴 PNG를 출력한다.

핵심 차별점은 **AI 이미지 생성을 사용하지 않는 것**이다. DUOMO가 정식 수입사로서 보유한 본사 룩북·자체 시공 사진을 라이브러리화해서 활용하기 때문에, 결과물이 "비슷한 분위기"가 아닌 **실제 정식 라인업의 진짜 사진**으로 만들어진다.

## 2. 목표 / 비목표

### 목표
- 카페24/폐쇄몰 상세페이지 이미지 생성 시간을 시간 단위에서 분 단위로 단축
- DUOMO 톤(premium-editorial — 차콜 + 워밍 골드 + 큰 여백)을 일관되게 유지
- 사내 자산(룩북 사진)을 재사용 가능한 라이브러리로 축적
- 디자이너 후작업이 필요 없는 수준의 1차 결과물 품질 확보
- 1.5주 안에 MVP 동작

### 비목표 (V2 이후 고려)
- 외부 파트너/고객 직접 접근
- 카페24 자동 업로드
- 작업 이력 검색·복제·버전 관리 (V1은 파일 목록만)
- 모바일 전용 UI
- 영문/다국어 카피
- A/B 카피 비교 도구
- PSD/Figma export
- AI 이미지 생성 폴백 (사진이 없는 경우는 V1에서 사용자 업로드로 강제)

## 3. 사용자 페르소나

| 페르소나 | 인원 | 사용 시나리오 |
|---|---|---|
| 마케팅 담당자 | 2~4명 | 신규 입고 라인업의 상세페이지 제작 (가장 자주) |
| 영업 담당자 | 3~5명 | 고객 제안용 단품 상세페이지 |
| 관리자 (관리자 페이지 권한) | 1~2명 | 룩북 라이브러리 업데이트, 신규 브랜드 추가 |
| 디자이너 | 1~2명 | 결과물 검수, 디자인 토큰 튜닝 피드백 |

전 사용자 인증: Google Workspace OAuth (도메인 한정).

## 4. 아키텍처

```
[Browser]
   ↓ HTTPS + Google OAuth (DUOMO 도메인만 허용)
[Cloud Run — Streamlit 컨테이너]
   │
   ├── pipeline/copy.py     → Anthropic Claude API (13섹션 카피 JSON 생성)
   ├── pipeline/library.py  → Google Drive API (룩북 인덱스 검색·다운로드)
   ├── pipeline/compose.py  → PIL (이미지 합성 + 타이포 렌더링)
   └── pipeline/stitch.py   → 13장 → 합본 PNG/PDF (기존 stitch_images.py 재활용)
   │
   ├── storage/drive.py     → Google Drive (라이브러리 + 결과물 공유 폴더)
   └── auth/google_oauth.py → Google OAuth 도메인 검증
```

**핵심 결정**:
- 기존 [`landing-page-generator`](../../../../../.claude/skills/landing-page-generator/) 스킬의 `agents/*.md`를 시스템 프롬프트로 그대로 로드 → 톤 가이드 100% 재사용
- 기존 [`scripts/stitch_images.py`](../../../../../.claude/skills/landing-page-generator/scripts/stitch_images.py) 재활용
- Gemini API 의존성 **제거**
- Secrets는 Cloud Run Secret Manager (Claude 키, Google OAuth 클라이언트, Drive 서비스 계정)

## 5. 사용자 플로우 (5단계)

```
1. 로그인 (Google Workspace OAuth, DUOMO 도메인 한정)
       ↓
2. 신규 프로젝트 / 최근 작업 (단순 파일 목록)
       ↓
3. 입력 폼
   ├── 브랜드 / 모델 / 디자이너 / 연식 / 가격 / 리드타임 / 한정 요소
   ├── 레퍼런스 이미지 업로드 (선택 — 라이브러리에 없는 경우)
   └── 톤 프리셋 (premium-editorial 기본, 4종 선택 가능)
       ↓
4. 카피 검토 (Claude가 13섹션 카피 JSON 생성)
   └── 사용자가 섹션별 텍스트 직접 편집 → 승인 ✓
       ↓
5. 이미지 생성·미리보기
   ├── 이미지 섹션(5~6개): 라이브러리 자동 매칭 → 상위 5장 썸네일 → 사용자 선택
   ├── 타이포 섹션(7~8개): 자동 렌더링 (선택 불필요)
   ├── 13섹션 전체 PIL 합성 (30초~1분)
   ├── 미리보기 + 섹션별 [재생성] 버튼
   └── 최종 합본 PNG → 다운로드 + Drive 공유 폴더로 자동 업로드
```

## 6. 핵심 기술 결정

### 6.1 이미지 라이브러리 — Google Drive + JSON 인덱스

DUOMO가 이미 Google Workspace를 사용하므로 Drive를 라이브러리 저장소로 활용한다.

```
Google Drive: /duomo/lookbook/
├── bb-italia/
│   ├── charles/
│   │   ├── living-001.jpg          ← 본사 룩북 (공간 사진)
│   │   ├── product-001.jpg         ← 본사 룩북 (제품 단독)
│   │   └── showroom-seoul-001.jpg  ← DUOMO 자체 촬영
│   └── ...
├── cassina/
├── flos/
└── _index.json                      ← 전체 메타데이터
```

`_index.json` 항목 스키마:

```json
{
  "id": "bbi-charles-living-001",
  "drive_id": "1aBcD...",
  "brand": "B&B Italia",
  "model": "Charles",
  "designer": "Antonio Citterio",
  "year": 1997,
  "type": "space",
  "section_fit": ["01_hero", "04_story", "13_final_cta"],
  "tags": ["modular", "sofa", "living", "natural-light"],
  "orientation": "landscape",
  "added_by": "admin@duomo",
  "added_at": "2026-05-26"
}
```

- `type` 열거: `space` (공간 사진) | `product` (제품 단독) | `detail` (디테일) | `showroom` (전시장)
- `section_fit` 열거: `01_hero` | `04_story` | `05_solution` | `06_how_it_works` | `08_authority` | `13_final_cta`
- 인덱스 업데이트는 `pages/3_library_admin.py`에서 5분 작업 수준의 UI로 처리
- Cloud Run에서 Drive API로 이미지 다운로드 → 로컬 `/tmp` 캐시 (컨테이너 재기동 시까지 유지)

### 6.2 자동 매칭 우선순위

```python
# pipeline/library.py
def find_images_for_section(brief, section_key, top_n=5):
    # 1순위: brand + model 정확 매칭
    candidates = [i for i in INDEX
                  if section_key in i["section_fit"]
                  and i["brand"] == brief["brand"]
                  and i["model"] == brief["model"]]
    # 2순위: brand만 매칭
    if not candidates:
        candidates = [i for i in INDEX
                      if section_key in i["section_fit"]
                      and i["brand"] == brief["brand"]]
    # 3순위: designer 매칭
    if not candidates:
        candidates = [i for i in INDEX
                      if section_key in i["section_fit"]
                      and i["designer"] == brief["designer"]]
    # 4순위: 섹션 적합성만
    if not candidates:
        candidates = [i for i in INDEX if section_key in i["section_fit"]]
    return candidates[:top_n]
```

매칭 결과 0장이면 사용자 업로드를 강제 (스킵 불가).

### 6.3 13섹션을 두 그룹으로 분리해서 렌더링

**그룹 A: 이미지 기반 섹션 (5~6개)** — Hero / Story / Solution / How It Works / Authority / Final CTA

```python
def render_image_section(canvas_size, ref_image, copy, design_tokens):
    bg = Image.open(ref_image).resize_and_crop(canvas_size)
    bg = apply_editorial_grade(bg)            # 채도 -10%, 워밍 톤
    if section_is_dark_inversion(key):
        bg = apply_overlay(bg, color="#1A1A1A", opacity=0.55)
    draw = ImageDraw.Draw(bg)
    draw_text_layers(draw, copy, design_tokens)
    return bg
```

**그룹 B: 타이포그래피 섹션 (7~8개)** — Problem / Pain / Social Proof / Benefits / Risk Removal / Comparison / Target Filter

```python
def render_typo_section(canvas_size, copy, design_tokens, mode="off-white"):
    bg = Image.new("RGB", canvas_size, "#FAFAF7" if mode == "off-white" else "#1A1A1A")
    draw = ImageDraw.Draw(bg)
    draw_typography_composition(draw, copy, design_tokens)
    return bg
```

폰트는 컨테이너에 번들:
- `Pretendard-Light.otf` (헤드라인 한글)
- `Pretendard-Medium.otf` (CTA 한글)
- `PlayfairDisplay-Regular.ttf` (브랜드명·디자이너명 영문)

디자인 토큰은 `~/.claude/skills/landing-page-generator/agents/04-design-direction.md`의 `premium-editorial` 프리셋을 JSON으로 추출 (`design_tokens/premium-editorial.json`).

### 6.4 카피 생성 — Anthropic Claude API 직접 호출

```python
# pipeline/copy.py
def generate_copy(brief: dict, research: dict) -> dict:
    system_prompt = Path("prompts/03-copy.md").read_text(encoding="utf-8")
    user_prompt = f"브리프:\n{json.dumps(brief, ensure_ascii=False, indent=2)}\n\n리서치:\n{json.dumps(research, ensure_ascii=False, indent=2)}\n\n13섹션 JSON을 생성해주세요. 출력은 JSON만."
    response = anthropic.messages.create(
        model="claude-sonnet-4-5",
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
        max_tokens=8000,
    )
    return json.loads(response.content[0].text)
```

리서치(`02-research.md`), 카피(`03-copy.md`), 디자인 방향(`04-design-direction.md`) 3개 에이전트를 Claude API 3회 호출로 순차 실행.

## 7. 디렉터리 구조

```
duomo-landing-tool/
├── app.py                      # Streamlit 엔트리, 라우팅
├── pages/
│   ├── 1_new_project.py        # 입력 → 카피 → 합성 위저드
│   ├── 2_history.py            # 최근 작업 (단순 파일 목록)
│   └── 3_library_admin.py      # 룩북 라이브러리 관리자 페이지
├── pipeline/
│   ├── __init__.py
│   ├── copy.py                 # Claude API 호출
│   ├── library.py              # Drive 인덱스 + 매칭 로직
│   ├── compose.py              # PIL 합성 (그룹 A + 그룹 B)
│   └── stitch.py               # 13장 → 합본 PNG/PDF
├── prompts/                    # ~/.claude/skills/landing-page-generator/agents/ 에서 복사
│   ├── 02-research.md
│   ├── 03-copy.md
│   └── 04-design-direction.md
├── design_tokens/
│   └── premium-editorial.json
├── fonts/
│   ├── Pretendard-Light.otf
│   ├── Pretendard-Medium.otf
│   └── PlayfairDisplay-Regular.ttf
├── auth/
│   └── google_oauth.py
├── storage/
│   └── drive.py                # Drive 업로드·다운로드·인덱스 입출력
├── tests/
│   ├── test_copy.py
│   ├── test_library.py
│   └── test_compose.py
├── Dockerfile
├── requirements.txt
├── README.md
└── docs/
    └── superpowers/specs/
        └── 2026-05-26-duomo-landing-tool-design.md  ← 이 문서
```

## 8. 데이터 모델

### 8.1 라이브러리 인덱스 (`_index.json`)
6.1절 스키마 참조.

### 8.2 카피 JSON (Claude 출력)
[`~/.claude/skills/landing-page-generator/agents/03-copy.md`](../../../../../.claude/skills/landing-page-generator/agents/03-copy.md)의 출력 형식 그대로:

```json
{
  "section_01_hero": {
    "headline_options": ["...", "...", "..."],
    "subheadline": "...",
    "urgency_badge": "...",
    "cta_text": "..."
  },
  ...
}
```

### 8.3 프로젝트 작업 (세션 상태)
Streamlit `st.session_state`에 저장. 컨테이너 재기동 시 손실 — V1은 다운로드를 통한 명시적 저장만 지원.

```python
st.session_state = {
    "brief": {...},
    "research": {...},
    "copy": {...},
    "selected_images": {  # 사용자가 라이브러리에서 선택한 이미지
        "01_hero": "bbi-charles-living-001",
        "04_story": ["...", "..."],  # Story는 BEFORE/AFTER 2장
        ...
    },
    "uploaded_images": {  # 사용자가 직접 업로드한 이미지
        "05_solution": "/tmp/uploads/.../product.jpg"
    },
    "rendered_sections": {  # 13섹션 PNG 파일 경로
        "01_hero": "/tmp/render/.../01_hero.png",
        ...
    }
}
```

## 9. 에러 핸들링

| 실패 지점 | 처리 |
|---|---|
| Google OAuth 도메인 외 사용자 | 로그인 거부 + 안내 메시지 |
| Drive API 호출 실패 | 3회 지수 백오프 재시도 → 로컬 캐시 사용 |
| Claude API 실패 (rate limit / 5xx) | 3회 재시도, 사용자에 진행상황 표시 |
| 카피 JSON 파싱 실패 | Claude에 "JSON only" 재요청 1회, 그래도 실패 시 수동 편집 모드로 폴백 |
| 라이브러리에 매칭 이미지 0장 | 사용자 업로드 강제 (스킵 불가) |
| 폰트 파일 미발견 | 시스템 폰트 폴백 + 로그 경고 |
| 업로드 이미지 손상 / 10MB 초과 | 자동 1024px 리사이즈, 10MB 초과 시 거부 |
| Cloud Run 60분 타임아웃 | PIL 합성은 빠르므로 거의 없음, 진행률 표시 |

모든 에러는 구조화 로그(JSON, level·timestamp·user·step)로 기록. 사용자 표시 메시지는 복구 정보 포함 (`무엇이·왜·어떻게`).

## 10. 테스트 전략

```
단위 테스트 (pytest):
  - pipeline/copy.py:    Claude 응답 모킹, JSON 파싱·검증, 필수 키 누락 시 폴백
  - pipeline/library.py: 매칭 우선순위 4단계, 인덱스 빈 경우 처리
  - pipeline/compose.py: PIL 합성 결과의 크기·색상·텍스트 위치 픽셀 샘플 검증

통합 테스트:
  - 모의 Drive(샘플 5장) + 모의 Claude → 전체 파이프라인 1회
  - 출력 합본 PNG가 1200×~7000px인지

스모크 테스트 (배포 전):
  - 실제 신상 1건으로 전체 흐름 1회
  - 디자이너가 결과물 시각적 검수

수동 QA (런칭 전):
  - DUOMO 실제 입고품 3건으로 테스트 (B&B Italia · Cassina · Flos 각 1건)
  - 라이브러리 자동 매칭 정확도 확인
```

## 11. 비용 추정

월 30건 페이지 생성 기준:

| 항목 | 월 비용 |
|---|---|
| Cloud Run (vCPU 1, 메모리 2GB, 사용량 기반) | ~$5 |
| Claude (Sonnet, 페이지당 ~$0.05) | ~$1.5 |
| Google Drive | $0 (Workspace 포함) |
| 폰트 (OFL 라이선스) | $0 |
| **총** | **~$7/월** |

(Gemini 포함안 ~$22/월 대비 약 70% 절감)

## 12. 일정 (1.5주 / 영업일 10일)

| 일차 | 작업 |
|---|---|
| Day 1~2 | 라이브러리 구조 설계, Drive API 연동, 인덱스 JSON 빌드 도구 |
| Day 3~5 | `pipeline/copy.py` (Claude), `pipeline/compose.py` (PIL 그룹 A·B 분리 합성) |
| Day 6~7 | Streamlit UI 3페이지, Google OAuth |
| Day 8 | Dockerfile, Cloud Run 배포, 스모크 테스트 |
| Day 9~10 | DUOMO 실제 신상 3건 수동 QA, 룩북 초기 30~50장 업로드 |

## 13. 위험 요소 & 완화책

| 위험 | 영향 | 완화 |
|---|---|---|
| 본사 룩북 사진을 충분히 확보 못 함 | 매칭 실패 → 사용자 업로드 부담 | 초기 30~50장(우선 입고 라인업)으로 시작, 점진 확장 |
| 디자이너가 결과물을 "어색하다"고 함 | 도구 사용률 저조 | 디자이너 1명을 V1 설계에 같이 태우기, MVP 후 피드백 |
| PIL 한글 자간/줄바꿈이 어색함 | 카피 가독성 저하 | 초기 합성 결과 50장 시각 검수, 디자인 토큰 튜닝 |
| 관리자 부재 시 라이브러리 정체 | 시간 지나면 새 모델 매칭 안 됨 | 관리자 페이지를 5분 작업 수준으로 단순화 |
| Streamlit 동시 사용자 10명+ 시 응답 저하 | 사용 경험 저하 | Cloud Run min-instance=1, max-instance=3 설정 |

## 14. 의사결정 기록 (Decision Log)

| 결정 | 대안 | 선택 이유 |
|---|---|---|
| **Gemini 이미지 생성 제거, 본사 룩북 사용** | Gemini API로 자동 생성 / 하이브리드 | 정식 수입사 정체성과 맞음, 결과물 정확도 ★★★, 비용 90% 절감, 한글 깨짐 0% |
| **Streamlit 선택** | Next.js + Supabase / Cloudflare Workers + FastAPI | 1~2주 MVP, Python 코드 재활용, 5~15명 내부 도구에 적합 |
| **Cloud Run 호스팅** | Streamlit Cloud / 자체 서버 | Google Workspace OAuth 연동 자연스러움, 사용량 기반 과금 |
| **Drive를 라이브러리 저장소로** | S3 / Supabase Storage / 컨테이너 볼륨 | 이미 Workspace 사용 중, 사진 업로드·공유가 자연스러움 |
| **카피 검토 + 섹션 재생성 워크플로 (B 옵션)** | 원샷 모드 (A) / 프로젝트 관리 (C) | 비용 절감 + 좋은 UX의 균형 |
| **MVP에서 작업 이력 DB 제외** | Postgres / SQLite 추가 | V1 단순화, 다운로드를 통한 명시적 저장으로 충분 |

## 15. V2 후보 (참고)

V1 검증 후 우선순위에 따라 검토:
- 작업 이력 DB (검색·복제·버전 관리)
- 외부 파트너 권한 (duomomall.cafe24.com 파트너 사장님 대상)
- Cafe24 자동 업로드 API 연동
- 다른 DUOMO 자동화 시스템과 통합 (제안서 자동생성, 카탈로그 시스템)
- AI 이미지 생성 폴백 (룩북에 없는 신상 미입고품 대응)
- A/B 카피 비교
- 영문/다국어 카피 (해외 파트너 대상)
- 모바일 친화 UI

---

## 다음 단계

1. 사용자(Paul) 스펙 검토 → 승인
2. `superpowers:writing-plans` 스킬로 구현 계획 수립
3. 구현 시작 (Day 1)
