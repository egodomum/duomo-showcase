"""최근 작업 — Drive 공유 폴더의 결과물 파일 목록 (또는 데모: 로컬 폴더)."""
from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

import streamlit as st
from googleapiclient.discovery import build as g_build

if not st.session_state.get("user_email"):
    st.error("먼저 로그인하세요.")
    st.stop()

DRIVE_OUTPUT_FOLDER_ID = os.getenv("DRIVE_OUTPUT_FOLDER_ID")
DEMO_MODE = os.getenv("DEMO_MODE", "").lower() in ("1", "true", "yes")

st.title("최근 작업")

if DEMO_MODE:
    # 로컬 출력 폴더(/tmp/duomo-render/<user>/)에서 PNG 목록
    local_dir = Path("/tmp/duomo-render") / st.session_state["user_email"]
    if not local_dir.exists():
        st.info("아직 만들어진 페이지가 없습니다.")
        st.stop()
    pngs = sorted(local_dir.glob("*.png"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not pngs:
        st.info("아직 만들어진 페이지가 없습니다.")
        st.stop()
    for p in pngs:
        col1, col2, col3 = st.columns([3, 2, 1])
        with col1:
            st.write(p.name)
        with col2:
            ts = datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
            st.caption(ts)
        with col3:
            with open(p, "rb") as f:
                st.download_button("다운로드", data=f, file_name=p.name,
                                   mime="image/png", key=f"dl_{p.name}")
    st.stop()

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
