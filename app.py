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
DEMO_MODE = os.getenv("DEMO_MODE", "").lower() in ("1", "true", "yes")

st.set_page_config(
    page_title="DUOMO Landing Tool",
    page_icon="📐",
    layout="wide",
)


def _gate_oauth() -> None:
    """OAuth 가드 — 미인증 사용자는 로그인 화면.

    DEMO_MODE=1이면 OAuth를 건너뛰고 가짜 사용자로 자동 로그인.
    """
    if st.session_state.get("user_email"):
        return

    if DEMO_MODE:
        st.session_state["user_email"] = "demo@duomo.local"
        st.session_state["credentials"] = None  # Drive 호출은 자동 폴백됨
        return

    if not (CLIENT_ID and CLIENT_SECRET):
        st.error("OAuth 환경변수가 설정되지 않았습니다. .env를 확인하거나 DEMO_MODE=1로 검증용 실행하세요.")
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

if DEMO_MODE:
    st.sidebar.warning("🧪 DEMO MODE")
st.sidebar.markdown(f"**{st.session_state['user_email']}**")
if st.sidebar.button("로그아웃"):
    st.session_state.clear()
    st.rerun()

st.title("DUOMO Landing Tool")
if DEMO_MODE:
    st.info(
        "🧪 **DEMO MODE** — OAuth와 Drive가 우회됩니다. "
        "라이브러리는 비어있으니 신규 프로젝트 → 3단계에서 이미지를 직접 업로드하세요."
    )
st.write("좌측 사이드바에서 페이지를 선택하세요.")
st.markdown("""
- **신규 프로젝트** — 새 상세페이지 만들기
- **최근 작업** — 지금까지 만든 페이지 목록
- **라이브러리 관리** — 본사 룩북 사진 업로드 (관리자)
""")
