"""신규 프로젝트 — 쇼케이스 블록 조립 위저드."""
from __future__ import annotations

import base64
import json as _json
import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from blocks.registry import list_blocks, get_block
from pipeline.recipe import new_recipe, add_block, remove_block, move_block
from render.accents import resolve_accent
from render.page_builder import build_page
from render.renderer import render_html_to_png

load_dotenv()

PROJECT = Path(__file__).parent.parent
FONTS = PROJECT / "fonts"
PROMPTS = PROJECT / "prompts"

if not st.session_state.get("user_email"):
    st.error("먼저 로그인하세요.")
    st.stop()

st.title("신규 상세페이지")

if "recipe" not in st.session_state:
    st.session_state.recipe = None
if "wizard_step" not in st.session_state:
    st.session_state.wizard_step = 1


def _claude():
    import anthropic
    return anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def _step1_meta():
    st.header("1단계 · 기본 정보")
    with st.form("meta"):
        c1, c2 = st.columns(2)
        with c1:
            brand = st.text_input("브랜드", placeholder="B&B Italia")
            product = st.text_input("제품명", placeholder="Camaleonda")
        with c2:
            designer = st.text_input("디자이너", placeholder="Mario Bellini")
            category = st.selectbox("카테고리", ["furniture", "lighting"])
        if st.form_submit_button("다음: 블록 조립", type="primary"):
            if not brand:
                st.error("브랜드는 필수입니다.")
                return
            st.session_state.recipe = new_recipe(
                brand=brand, product=product, designer=designer,
                category=category, accent=resolve_accent(brand))
            st.session_state.wizard_step = 2
            st.rerun()
    st.caption("브랜드를 입력하면 액센트 컬러가 자동 적용됩니다 (골드 없음).")


def _step2_compose():
    r = st.session_state.recipe
    st.header("2단계 · 블록 조립")
    st.caption(f"브랜드: {r['meta']['brand']} · 액센트: {r['meta']['accent']}")

    specs = {s.label: s.type for s in list_blocks()}
    hint = ("가구: brand·designer·hero·intro·material·color_options·dimension·closing 권장"
            if r["meta"]["category"] == "furniture"
            else "조명: brand·designer·hero·intro·color_options·spec_table·dimension·closing 권장")
    st.info(hint)
    pick = st.selectbox("블록 추가", list(specs.keys()))
    if st.button("+ 추가"):
        add_block(r, specs[pick])
        st.rerun()

    st.markdown("---")
    if not r["blocks"]:
        st.write("아직 블록이 없습니다. 위에서 추가하세요.")
    for i, blk in enumerate(r["blocks"]):
        c1, c2, c3, c4 = st.columns([5, 1, 1, 1])
        with c1:
            st.write(f"**{i+1}. {blk['type']}**")
        with c2:
            if st.button("↑", key=f"up{i}"):
                move_block(r, i, -1); st.rerun()
        with c3:
            if st.button("↓", key=f"dn{i}"):
                move_block(r, i, +1); st.rerun()
        with c4:
            if st.button("✕", key=f"rm{i}"):
                remove_block(r, i); st.rerun()

    st.markdown("---")
    cols = st.columns(2)
    with cols[0]:
        if st.button("← 기본 정보"):
            st.session_state.wizard_step = 1; st.rerun()
    with cols[1]:
        if st.button("다음: 데이터 입력 →", type="primary", disabled=not r["blocks"]):
            st.session_state.wizard_step = 3; st.rerun()


def _collect_refs(r) -> dict:
    refs = {}
    for i, blk in enumerate(r["blocks"]):
        ref_key = blk["data"].get("ref")
        img_bytes = st.session_state.get(f"imgbytes_{i}")
        if ref_key and img_bytes is not None:
            b64 = base64.b64encode(img_bytes).decode()
            refs[ref_key] = f"data:image/jpeg;base64,{b64}"
    return refs


def _step3_data():
    r = st.session_state.recipe
    st.header("3단계 · 데이터 입력 & 렌더")

    for i, blk in enumerate(r["blocks"]):
        spec = get_block(blk["type"]).spec
        with st.expander(f"{i+1}. {spec.label} ({blk['type']})", expanded=False):
            if spec.copy_schema and st.button("✨ 카피 생성", key=f"gen{i}"):
                from pipeline.copy import generate_block_copy, CopyError
                try:
                    out = generate_block_copy(
                        client=_claude(), block_type=blk["type"],
                        copy_schema=spec.copy_schema, meta=r["meta"],
                        system_prompt_path=PROMPTS / "showcase-copy.md")
                    blk["data"].update(out)
                    st.rerun()
                except CopyError as e:
                    st.error(f"카피 생성 실패: {e}")
            for f in spec.input_fields:
                cur = blk["data"].get(f.key, "")
                if f.kind == "textarea":
                    blk["data"][f.key] = st.text_area(
                        f.label, value=cur, key=f"f_{i}_{f.key}")
                elif f.kind == "image":
                    up = st.file_uploader(f.label, type=["jpg", "jpeg", "png"],
                                          key=f"up_{i}_{f.key}")
                    if up is not None:
                        st.session_state[f"imgbytes_{i}"] = up.read()
                        blk["data"][f.key] = f"ref_{i}"
                elif f.kind == "list":
                    st.caption(f"{f.label} — JSON으로 입력")
                    raw = st.text_area(f.label, value=_json.dumps(cur or [], ensure_ascii=False),
                                       key=f"l_{i}_{f.key}")
                    try:
                        blk["data"][f.key] = _json.loads(raw)
                    except Exception:
                        st.warning("리스트 JSON 형식 오류")
                else:
                    blk["data"][f.key] = st.text_input(
                        f.label, value=cur, key=f"f_{i}_{f.key}")

    st.markdown("---")
    if st.button("🎨 상세페이지 렌더", type="primary"):
        refs = _collect_refs(r)
        html = build_page(r, fonts_dir=FONTS, refs=refs)
        out_dir = Path("/tmp/duomo-showcase") / st.session_state["user_email"]
        out_dir.mkdir(parents=True, exist_ok=True)
        out = out_dir / "page.png"
        with st.spinner("렌더링 중..."):
            render_html_to_png(html, out)
        st.session_state.rendered_path = str(out)
        st.rerun()

    if st.session_state.get("rendered_path"):
        st.image(st.session_state.rendered_path, use_container_width=True)
        with open(st.session_state.rendered_path, "rb") as fh:
            st.download_button("📥 PNG 다운로드", data=fh,
                               file_name=f"{r['meta'].get('product','duomo')}.png",
                               mime="image/png")

    if st.button("← 블록 조립"):
        st.session_state.wizard_step = 2; st.rerun()


step = st.session_state.wizard_step
if step == 1 or st.session_state.recipe is None:
    _step1_meta()
elif step == 2:
    _step2_compose()
else:
    _step3_data()
