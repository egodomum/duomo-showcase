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
