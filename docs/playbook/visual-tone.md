# DUOMO 비주얼 톤 플레이북 (Figma 실측)

> 출처: DUOMO 실제 Figma — Artemide Onfale 상세페이지 ([파일](https://www.figma.com/design/MKUGdEfBv7plKKq3UpwbBE/Artemide))
> 분석한 섹션: Hero(제품+제품명), 브랜드 스테이트먼트, 옵션/색상 스펙
> 추출일: 2026-06-25

---

## 0. 한 줄 요약

> DUOMO 상세페이지는 "매거진"이 아니라 **"e커머스 디테일 페이지"**다.
> **순백 배경 · 전부 중앙 정렬 · 큰 글씨 · 브랜드 컬러 액센트 · 거대한 여백.**

우리가 초기에 만든 premium-editorial(좌측정렬·오프화이트·골드·1200px·17px 본문)은
**잡지 톤**이라 DUOMO 실제와 다르다. 카페24/29CM/SSG에 올리는 1000px 폭 상세 이미지엔
아래 실측 스펙을 따라야 한다.

---

## 1. 캔버스

| 항목 | DUOMO 실측 | 비고 |
|---|---|---|
| 폭 | **1000px** (주력), 750px(일부 채널) | 모바일 우선 e커머스. 우리 기존 1200px과 다름 |
| 정렬 | **전부 중앙 정렬** | 좌측정렬 아님 |
| 섹션 패딩(상하) | **270px** (py-270) | 극단적 여백이 고급감의 핵심 |
| 섹션 내 요소 간격 | 44~84px | |

## 2. 컬러 (Figma 변수명 그대로)

| 토큰 | 값 | 용도 |
|---|---|---|
| 배경 | **#FFFFFF** (순백) | 콘텐츠 섹션 배경. 오프화이트 아님 |
| gray/20 | **#2C2C2C** | 본문 텍스트 (따뜻한 검정) |
| gray/50 | #838486 | 보조 텍스트 |
| gray/70 | #C4C4C4 | 보더·구분선·색상 스와치 테두리 |
| brand/* | **브랜드별 컬러** (예: Artemide #DE0515) | 로고·액센트. **골드 고정 아님** |
| 사진 위 텍스트 | #FFFFFF | Hero 등 풀블리드 사진 위 |

→ 핵심: **액센트는 골드가 아니라 그 브랜드의 고유색.** B&B Italia·Cassina·Flos마다 다름.

## 3. 타이포그래피 (Figma 스타일 그대로)

| 스타일명 | 폰트 | 크기(1000px 기준) | 행간 | 자간 | 용도 |
|---|---|---|---|---|---|
| Headline/H1 | **Noto Serif Display SemiBold** | 106px | 1.0 | 0 | 제품명 (예: "Onfale") |
| Headline/H2 | Noto Serif Display SemiBold | 80px | 1.0 | 0 | 변형명 (예: "Piccolo") |
| Subheadline/S2 | Pretendard SemiBold | 40px | 1.0 | 0 | 섹션 라벨 (예: "색상") |
| Body/B1_regular | Pretendard Regular | 40px | 1.44 | -0.8 | Hero 한글 서브카피 |
| Body/B1_medium | Pretendard Medium | 40px | 1.44 | -0.8 | 브랜드 스테이트먼트 본문 |
| Paragraph/P2_medium | Pretendard Medium | 32px | 1.0 | 0 | 옵션 값 (예: "White") |

핵심 발견:
- **세리프 = Noto Serif Display** (Playfair 아님!). Noto Serif Display는 **한글도 지원** → 제품명을 한글로 써도 됨
- **본문이 40px** — 우리 기존 17px의 약 2.4배. 모바일 상세 이미지라 크게
- 영문 브랜드/제품명은 **세리프**, 한글 카피는 **Pretendard 산세리프**로 분리

## 4. 섹션 구성 패턴 (실측)

관찰된 섹션 유형:

**A. Hero (풀블리드 제품 사진 + 텍스트 오버레이)**
- 제품 사진이 화면 전체
- 하단 중앙에 텍스트 블록: [한글 서브카피 40px] → [제품명 세리프 106px] → [변형명 세리프 80px]
- 텍스트는 흰색, 중앙 정렬, 세로로 쌓임 (gap 32px)

**B. 브랜드 스테이트먼트 (순백 배경)**
- 상단: 브랜드 로고 (벡터, 브랜드 컬러)
- 중앙: 큰 따옴표(") 장식 → 브랜드 철학 한글 3줄 (Pretendard Medium 40px, #2C2C2C) → 닫는 따옴표
- 전부 중앙 정렬, 위아래 270px 여백
- 예: "Artemide는 '빛을 통한 인간의 편안하고 자연스러운 경험'을 추구하며 전 세계 조명 디자인 분야를 선도하는 기업입니다."

**C. 옵션/스펙 (순백 배경)**
- 둥근 모서리 카드(radius ≈ 폭의 11.6%, 920px→107px)에 제품 사진
- 아래 중앙: 라벨(Pretendard SemiBold 40px "색상") → 옵션 (원형 스와치 + 값 "White" 32px)
- 색상 스와치 = 52px 원, #C4C4C4 테두리

추가로 파일에 존재(미분석): 갤러리 이미지, 사이즈 비교(Grande/Medio/Piccolo), 채널 배지(29CM·SSG·LF·S.I VILLAGE·쿠팡), 가이드 섹션.

## 5. 우리 기존 디자인과의 차이 (반드시 반영)

| 항목 | 기존 premium-editorial | DUOMO 실측 → 바꿀 것 |
|---|---|---|
| 폭 | 1200px | **1000px** |
| 배경 | 오프화이트 #FAFAF7 | **순백 #FFFFFF** |
| 정렬 | 좌측 | **중앙** |
| 본문 크기 | 17px | **40px** |
| 액센트 | 골드 #B8975A 고정 | **브랜드별 컬러** |
| 세리프 | Playfair Display (한글 ✗) | **Noto Serif Display** (한글 ✓) |
| 본문색 | #1A1A1A | **#2C2C2C** |
| 섹션 여백 | 140px | **270px** |

## 6. 적용 체크리스트

- [ ] 캔버스 1000px 폭으로
- [ ] 모든 텍스트 중앙 정렬
- [ ] 배경 순백, 본문 #2C2C2C
- [ ] 본문 40px / 라벨 40px SemiBold / 제품명 세리프 106px
- [ ] 세리프는 Noto Serif Display (한글 지원)
- [ ] 액센트는 해당 브랜드 고유색 (브리프에 brand_color 추가 필요)
- [ ] 섹션 상하 여백 크게 (목표 270px, 짧은 섹션은 비례 축소)
- [ ] 브랜드 스테이트먼트엔 따옴표 장식 + 철학 문장
- [ ] 옵션 섹션은 라벨 + 원형 스와치 패턴

## 7. 폰트 확보 필요

- ✅ Pretendard (있음)
- ❌ **Noto Serif Display** — 다운로드 필요. Google Fonts(OFL), 한글 글리프 포함 버전 확인
  - https://fonts.google.com/noto/specimen/Noto+Serif+Display
  - 단, Noto Serif Display는 라틴 위주. 한글 제목엔 **Noto Serif KR**가 더 적합할 수 있음 → 실제 Figma는 라틴 제품명에만 세리프를 써서 문제 없음
