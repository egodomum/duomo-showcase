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
