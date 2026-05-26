"""최근 작업 — Drive 공유 폴더의 결과물 파일 목록."""
from __future__ import annotations

import os
from pathlib import Path

import streamlit as st
from googleapiclient.discovery import build as g_build

if not st.session_state.get("user_email"):
    st.error("먼저 로그인하세요.")
    st.stop()

DRIVE_OUTPUT_FOLDER_ID = os.getenv("DRIVE_OUTPUT_FOLDER_ID")

st.title("최근 작업")

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
