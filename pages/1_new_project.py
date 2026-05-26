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


import anthropic
from pipeline.copy import generate_research, generate_copy, generate_design_direction, CopyError

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


@st.cache_resource
def _claude_client():
    return anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def _step2_copy():
    st.header("2단계 · 카피 검토 및 편집")

    if "copy_data" not in st.session_state:
        client = _claude_client()
        with st.spinner("리서치 생성 중... (약 30초)"):
            try:
                research = generate_research(
                    client=client,
                    brief=st.session_state.brief,
                    system_prompt_path=PROMPTS_DIR / "02-research.md",
                )
                st.session_state.research = research
            except CopyError as e:
                st.error(f"리서치 생성 실패: {e}")
                return

        with st.spinner("카피 생성 중... (약 60초)"):
            try:
                copy_data = generate_copy(
                    client=client,
                    brief=st.session_state.brief,
                    research=st.session_state.research,
                    system_prompt_path=PROMPTS_DIR / "03-copy.md",
                )
                st.session_state.copy_data = copy_data
            except CopyError as e:
                st.error(f"카피 생성 실패: {e}")
                return

        with st.spinner("디자인 방향 결정 중..."):
            try:
                design = generate_design_direction(
                    client=client,
                    brief=st.session_state.brief,
                    research=st.session_state.research,
                    system_prompt_path=PROMPTS_DIR / "04-design-direction.md",
                )
                st.session_state.design = design
            except CopyError as e:
                st.error(f"디자인 방향 실패: {e}")
                return

    # 카피 편집 UI
    edited = {}
    for section_key, content in st.session_state.copy_data.items():
        with st.expander(f"📝 {section_key}", expanded=False):
            edited_content = {}
            for field, value in content.items():
                if isinstance(value, list):
                    text = "\n".join(value)
                    new_text = st.text_area(
                        field, value=text, key=f"{section_key}_{field}", height=80,
                    )
                    edited_content[field] = [
                        line for line in new_text.split("\n") if line.strip()
                    ]
                elif isinstance(value, dict):
                    st.json(value)
                    edited_content[field] = value
                else:
                    edited_content[field] = st.text_input(
                        field, value=str(value), key=f"{section_key}_{field}",
                    )
            edited[section_key] = edited_content

    col_a, col_b = st.columns([1, 1])
    with col_a:
        if st.button("← 브리프로 돌아가기"):
            st.session_state.wizard_step = 1
            del st.session_state["copy_data"]
            st.rerun()
    with col_b:
        if st.button("이미지 생성 →", type="primary"):
            st.session_state.copy_data = edited
            st.session_state.wizard_step = 3
            st.rerun()


from pipeline.library import LibraryRepository
from pipeline.compose import render_section, load_tokens
from pipeline.stitch import stitch_sections, SECTION_ORDER
from storage.drive import DriveClient

from googleapiclient.discovery import build as g_build


DRIVE_LOOKBOOK_INDEX_ID = os.getenv("DRIVE_LOOKBOOK_INDEX_ID")
DRIVE_OUTPUT_FOLDER_ID = os.getenv("DRIVE_OUTPUT_FOLDER_ID")
FONTS_DIR = Path(__file__).parent.parent / "fonts"
TOKENS_PATH = Path(__file__).parent.parent / "design_tokens" / "premium-editorial.json"


@st.cache_resource
def _drive_client():
    """현재 세션 credentials로 Drive 클라이언트 생성."""
    creds = st.session_state.get("credentials")
    if not creds:
        return None
    service = g_build("drive", "v3", credentials=creds)
    cache_dir = Path("/tmp/duomo-drive-cache")
    return DriveClient(service=service, cache_dir=cache_dir)


@st.cache_resource
def _library_repo():
    drive = _drive_client()
    if not drive or not DRIVE_LOOKBOOK_INDEX_ID:
        return None
    return LibraryRepository(
        drive=drive,
        index_drive_id=DRIVE_LOOKBOOK_INDEX_ID,
        cache_dir=Path("/tmp/duomo-library-cache"),
    )


def _step3_compose():
    st.header("3단계 · 이미지 선택 및 합성")
    tokens = load_tokens(TOKENS_PATH)
    repo = _library_repo()

    if "section_choices" not in st.session_state:
        # 이미지 섹션 자동 매칭 초기화
        st.session_state.section_choices = {}
        for section_key, cfg in tokens["sections"].items():
            if cfg["mode"] in ("image", "image_split"):
                if repo:
                    matches = repo.find_for_section(
                        st.session_state.brief, section_key, top_n=5,
                    )
                else:
                    matches = []
                st.session_state.section_choices[section_key] = {
                    "candidates": matches,
                    "selected_drive_id": matches[0]["drive_id"] if matches else None,
                    "uploaded_path": None,
                }

    # 이미지 섹션별 선택 UI
    for section_key, cfg in tokens["sections"].items():
        if cfg["mode"] not in ("image", "image_split"):
            continue
        with st.expander(f"🖼️ {section_key} (이미지)", expanded=False):
            choice = st.session_state.section_choices[section_key]
            if choice["candidates"]:
                labels = [f"{c['brand']} / {c.get('model','-')} / {c['id']}"
                          for c in choice["candidates"]]
                sel = st.radio(
                    "라이브러리에서 선택", labels, key=f"radio_{section_key}",
                    index=0,
                )
                sel_idx = labels.index(sel)
                choice["selected_drive_id"] = choice["candidates"][sel_idx]["drive_id"]
            else:
                st.warning("라이브러리 매칭 없음. 직접 업로드하세요.")
            upl = st.file_uploader(
                "또는 직접 업로드 (선택 시 라이브러리보다 우선)",
                type=["jpg", "jpeg", "png"], key=f"upl_{section_key}",
            )
            if upl:
                p = Path("/tmp/duomo-uploads") / st.session_state["user_email"] / f"{section_key}_{upl.name}"
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(upl.read())
                choice["uploaded_path"] = str(p)

    st.markdown("---")
    if st.button("🎨 13섹션 합성", type="primary"):
        _render_all_sections(tokens, repo)
        st.session_state.rendered = True

    if st.session_state.get("rendered"):
        _show_previews()
        st.markdown("---")
        if st.button("📦 합본 PNG 생성 + 다운로드", type="primary"):
            _stitch_and_offer_download()


def _render_all_sections(tokens, repo):
    drive = _drive_client()
    fonts_dir = FONTS_DIR
    out_dir = Path("/tmp/duomo-render") / st.session_state["user_email"]
    out_dir.mkdir(parents=True, exist_ok=True)
    st.session_state.rendered_paths = {}

    progress = st.progress(0.0)
    sections = list(tokens["sections"].items())
    for i, (section_key, cfg) in enumerate(sections):
        progress.progress((i + 1) / len(sections), text=f"렌더링 중: {section_key}")
        # 이미지 경로 결정
        ref_paths = []
        if cfg["mode"] in ("image", "image_split"):
            choice = st.session_state.section_choices.get(section_key, {})
            if choice.get("uploaded_path"):
                ref_paths = [Path(choice["uploaded_path"])]
            elif choice.get("selected_drive_id") and drive:
                ref_paths = [drive.download(choice["selected_drive_id"])]
        copy_data = st.session_state.copy_data.get(f"section_{section_key}", {})
        try:
            img = render_section(
                section_key=section_key,
                copy_data=copy_data,
                tokens=tokens,
                fonts_dir=fonts_dir,
                ref_images=ref_paths,
            )
            out_path = out_dir / f"{section_key}.png"
            img.save(out_path, "PNG")
            st.session_state.rendered_paths[section_key] = out_path
        except Exception as e:
            st.error(f"{section_key} 렌더링 실패: {e}")


def _show_previews():
    st.subheader("미리보기")
    for section_key in SECTION_ORDER:
        path = st.session_state.rendered_paths.get(section_key)
        if not path:
            continue
        col1, col2 = st.columns([4, 1])
        with col1:
            st.image(str(path), use_container_width=True, caption=section_key)
        with col2:
            if st.button(f"🔄 재생성", key=f"regen_{section_key}"):
                tokens = load_tokens(TOKENS_PATH)
                # 단일 섹션 재렌더
                cfg = tokens["sections"][section_key]
                drive = _drive_client()
                ref_paths = []
                if cfg["mode"] in ("image", "image_split"):
                    choice = st.session_state.section_choices.get(section_key, {})
                    if choice.get("uploaded_path"):
                        ref_paths = [Path(choice["uploaded_path"])]
                    elif choice.get("selected_drive_id") and drive:
                        ref_paths = [drive.download(choice["selected_drive_id"])]
                copy_data = st.session_state.copy_data.get(f"section_{section_key}", {})
                try:
                    img = render_section(
                        section_key=section_key, copy_data=copy_data,
                        tokens=tokens, fonts_dir=FONTS_DIR, ref_images=ref_paths,
                    )
                    img.save(path, "PNG")
                    st.rerun()
                except Exception as e:
                    st.error(f"재생성 실패: {e}")


def _stitch_and_offer_download():
    out = Path("/tmp/duomo-render") / st.session_state["user_email"] / "final.png"
    stitch_sections(st.session_state.rendered_paths, out)
    st.success(f"합본 생성 완료: {out}")
    with open(out, "rb") as f:
        st.download_button(
            "📥 합본 PNG 다운로드",
            data=f, file_name="duomo_landing.png", mime="image/png",
        )

    # Drive 자동 업로드
    drive = _drive_client()
    if drive and DRIVE_OUTPUT_FOLDER_ID:
        try:
            file_id = drive.upload(
                out, DRIVE_OUTPUT_FOLDER_ID,
                name=f"{st.session_state.brief.get('brand','x')}_{st.session_state.brief.get('model','x')}_landing.png",
            )
            st.info(f"Drive 업로드 완료: {file_id}")
        except Exception as e:
            st.warning(f"Drive 업로드 실패: {e}")


# 라우팅 업데이트
if st.session_state.wizard_step == 1:
    _step1_brief()
elif st.session_state.wizard_step == 2:
    _step2_copy()
elif st.session_state.wizard_step == 3:
    _step3_compose()
else:
    st.error(f"알 수 없는 단계: {st.session_state.wizard_step}")
    if st.button("처음으로"):
        for k in ["wizard_step", "copy_data", "research", "design",
                  "section_choices", "rendered", "rendered_paths"]:
            st.session_state.pop(k, None)
        st.rerun()
