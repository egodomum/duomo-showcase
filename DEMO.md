# DEMO_MODE 검증 가이드

OAuth와 Google Drive 셋업 없이 도구를 빠르게 검증하는 방법.

## 셋업 (5분)

### 1. Anthropic API 키 발급
https://console.anthropic.com → API Keys → 키 발급 (결제 카드 등록 필요, $5부터)

### 2. .env 파일 생성

프로젝트 루트에서:
```bash
cp .env.example .env
```

`.env` 편집 — **딱 두 줄만** 수정:
```
DEMO_MODE=1
ANTHROPIC_API_KEY=sk-ant-...   # ← 발급받은 키
```

나머지 OAuth·Drive 변수는 그대로 둬도 됩니다 (DEMO_MODE에서 무시됨).

### 3. 의존성 확인

```bash
pip install -r requirements.txt
```

(Pillow, streamlit, anthropic 등 이미 설치되어 있으면 스킵)

### 4. 실행

```bash
streamlit run app.py
```

브라우저가 자동으로 http://localhost:8501 을 엽니다.

---

## 검증 흐름 (10~15분)

### 0. 첫 화면
- 로그인 없이 바로 메인 화면 진입 (사이드바에 🧪 DEMO MODE 배지 + `demo@duomo.local` 사용자)
- "🧪 DEMO MODE — OAuth와 Drive가 우회됩니다..." 안내가 보이면 정상

### 1. 신규 프로젝트 → Step 1: 브리프 입력
좌측 사이드바 **"1 new project"** 클릭. 예시 입력:

| 필드 | 값 |
|---|---|
| 브랜드 * | B&B Italia |
| 모델 * | Charles |
| 디자이너 | Antonio Citterio |
| 디자인 연식 | 1997 |
| 한 줄 정의 | 미니멀리즘의 정의 |
| 타겟 고객 | 자가 거주 30~50대, 안목 있는 |
| 공식가 | 18,400,000원~ |
| 리드타임 | 14~18주 |
| 핵심 가치 | 30년 가는 정통, 정식 수입 진품 보증, 5년 A/S |
| 한정 요소 | 2026 봄 시즌 한정 패브릭, 국내 12세트 |

레퍼런스 이미지는 Step 1에서 안 올려도 OK. → "카피 생성" 클릭.

### 2. Step 2: 카피 검토
약 1~2분 대기. Claude가 13섹션 카피를 생성하고 expander로 보여줍니다.
각 섹션을 펼쳐서 텍스트를 자유롭게 편집하세요. 마음에 들면 "이미지 생성 →" 클릭.

### 3. Step 3: 이미지 선택 + 합성
DEMO_MODE에서는 라이브러리 매칭이 없으므로, **이미지 6개 섹션마다 "라이브러리 매칭 없음. 직접 업로드하세요" 경고**가 뜹니다.

각 expander(`01_hero`, `04_story`, `05_solution`, `06_how_it_works`, `08_authority`, `13_final_cta`)에서 본인 PC에 있는 사진 1장씩 업로드:
- **공간 사진** (Hero/Story/FinalCTA): 본사 공식 룩북 카탈로그의 거실 인테리어 컷
- **제품 사진** (Solution): 단독 제품 컷
- **프로세스 사진** (HowItWorks): 전시장/시공/공장 같은 다큐멘터리 컷
- **전시장 사진** (Authority): DUOMO 매장 사진

→ "🎨 13섹션 합성" 클릭. 약 30초~1분 PIL 렌더링.

### 4. 미리보기 + 다운로드
13섹션 미리보기가 표시됩니다.
- 마음에 안 드는 섹션은 "🔄 재생성" 버튼 (현재 데이터로 다시 그림)
- 모든 섹션 OK면 "📦 합본 PNG 생성 + 다운로드" 클릭
- 1200×~7500px 합본 PNG가 다운로드됨

### 5. 최근 작업 확인
사이드바 **"2 history"** → DEMO_MODE에서는 로컬 폴더(`/tmp/duomo-render/demo@duomo.local/`)의 PNG 파일 목록.

---

## 비용

검증 1건당 약:
- Claude (research + copy + design): ~$0.05
- Drive: $0 (DEMO_MODE에서 미사용)
- **총 ~$0.05** (50원 정도)

3~5건 검증해보고 결과 퀄리티를 평가하세요.

---

## 검증 후

만족스러우면 → 정식 배포 절차 (`deploy/README.md` 참조)로 OAuth·Drive 셋업 후 사내 운영 시작.

검증 결과 카피 톤이나 디자인 토큰을 조정하고 싶으면:
- 카피 톤: `prompts/03-copy.md` 직접 편집
- 디자인 토큰: `design_tokens/premium-editorial.json` 직접 편집
- 변경 후 `streamlit run app.py` 재실행 (자동 reload)

---

## 흔한 문제

| 증상 | 원인 / 해결 |
|---|---|
| "OAuth 환경변수가 설정되지 않았습니다" 에러 | `DEMO_MODE=1`이 .env에 없거나 잘못 입력 |
| 카피 생성 단계에서 401 에러 | `ANTHROPIC_API_KEY` 누락 또는 잘못된 키 |
| 카피 생성 단계에서 한참 대기 | 정상 — 13섹션 카피는 60~120초 소요 |
| 한글이 □ 또는 ?로 표시 | 폰트 파일이 `fonts/` 폴더에 없음. `Get-ChildItem fonts/` 확인 |
| Step 3에서 모든 섹션이 빈 화면 | 이미지를 업로드하지 않았음. 모든 이미지 섹션(6개)에 1장씩 업로드 필수 |
| 합본 다운로드 후 카페24에 올렸는데 모바일에서 너무 작음 | 1200px PNG는 카페24 기본 컨테이너 너비. CSS로 max-width: 100% 설정 |
