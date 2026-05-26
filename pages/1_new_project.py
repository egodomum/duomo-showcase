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
