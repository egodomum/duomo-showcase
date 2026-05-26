"""라이브러리 관리자 — 본사 룩북 이미지 업로드 + 메타데이터 입력."""
from __future__ import annotations

import os
import json
from datetime import datetime
from pathlib import Path

import streamlit as st
from googleapiclient.discovery import build as g_build

from storage.drive import DriveClient
from pipeline.library import load_index

if not st.session_state.get("user_email"):
    st.error("먼저 로그인하세요.")
    st.stop()

DRIVE_LOOKBOOK_FOLDER_ID = os.getenv("DRIVE_LOOKBOOK_FOLDER_ID")
DRIVE_LOOKBOOK_INDEX_ID = os.getenv("DRIVE_LOOKBOOK_INDEX_ID")

st.title("라이브러리 관리")
st.caption("본사 룩북·DUOMO 자체 촬영 사진을 업로드하고 인덱스에 등록합니다.")

if not (DRIVE_LOOKBOOK_FOLDER_ID and DRIVE_LOOKBOOK_INDEX_ID):
    st.error("DRIVE_LOOKBOOK_FOLDER_ID, DRIVE_LOOKBOOK_INDEX_ID 환경변수 설정 필요")
    st.stop()

creds = st.session_state.get("credentials")
service = g_build("drive", "v3", credentials=creds)
drive = DriveClient(
    service=service, cache_dir=Path("/tmp/duomo-library-cache"),
)


def _load_index_from_drive() -> list[dict]:
    local = drive.download(DRIVE_LOOKBOOK_INDEX_ID, mime_suffix=".json")
    return load_index(local)


def _save_index_to_drive(items: list[dict]) -> None:
    """인덱스 JSON을 Drive에 업데이트."""
    tmp = Path("/tmp/_index.json")
    tmp.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
    from googleapiclient.http import MediaFileUpload
    media = MediaFileUpload(str(tmp), mimetype="application/json")
    service.files().update(fileId=DRIVE_LOOKBOOK_INDEX_ID, media_body=media).execute()


tab1, tab2 = st.tabs(["새 이미지 추가", "기존 인덱스 보기"])

with tab1:
    with st.form("library_upload"):
        st.subheader("이미지 + 메타데이터 입력")
        col1, col2 = st.columns(2)
        with col1:
            brand = st.text_input("브랜드 *", placeholder="B&B Italia")
            model = st.text_input("모델", placeholder="Charles")
            designer = st.text_input("디자이너", placeholder="Antonio Citterio")
            year = st.number_input("디자인 연식", min_value=1900, max_value=2100,
                                   value=2000, step=1)
        with col2:
            img_type = st.selectbox("타입 *",
                                    ["space", "product", "detail", "showroom"])
            orientation = st.selectbox("방향", ["landscape", "portrait", "square"])
            section_fit = st.multiselect(
                "적합 섹션 *",
                ["01_hero", "04_story", "05_solution", "06_how_it_works",
                 "08_authority", "13_final_cta"],
            )
            tags_text = st.text_input("태그 (콤마 구분)",
                                      placeholder="modular, sofa, living")

        file = st.file_uploader("이미지 파일 *", type=["jpg", "jpeg", "png"])
        submitted = st.form_submit_button("Drive에 업로드 + 인덱스 등록",
                                          type="primary")
        if submitted:
            if not (brand and img_type and section_fit and file):
                st.error("필수 항목(* 표시) 입력 필요")
            else:
                tmp = Path("/tmp/upload") / file.name
                tmp.parent.mkdir(parents=True, exist_ok=True)
                tmp.write_bytes(file.read())
                with st.spinner("Drive 업로드 중..."):
                    drive_id = drive.upload(tmp, DRIVE_LOOKBOOK_FOLDER_ID,
                                            name=file.name)
                item_id = f"{brand.lower().replace(' ', '-')}-{(model or 'x').lower()}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                new_item = {
                    "id": item_id,
                    "drive_id": drive_id,
                    "brand": brand,
                    "model": model or None,
                    "designer": designer or None,
                    "year": int(year) if year else None,
                    "type": img_type,
                    "section_fit": section_fit,
                    "tags": [t.strip() for t in tags_text.split(",") if t.strip()],
                    "orientation": orientation,
                    "added_by": st.session_state["user_email"],
                    "added_at": datetime.now().strftime("%Y-%m-%d"),
                }
                with st.spinner("인덱스 업데이트 중..."):
                    items = _load_index_from_drive()
                    items.append(new_item)
                    _save_index_to_drive(items)
                st.success(f"등록 완료: {item_id}")

with tab2:
    items = _load_index_from_drive()
    st.info(f"총 {len(items)}장 등록")
    for it in items[-20:]:
        st.write(f"**{it['brand']}** / {it.get('model','-')} — {it['type']} — "
                 f"적합섹션 {it['section_fit']} — by {it['added_by']}")
