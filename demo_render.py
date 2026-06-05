"""DEMO 렌더링 스크립트 — Claude API 없이 13섹션 합성을 검증한다.

사실적인 fake copy로 B&B Italia Charles 소파 상세페이지를 한 번 완성한다.
실제 운영에서는 Claude가 이 JSON을 생성하지만, 여기서는 코드 박혀있음.
"""
from __future__ import annotations

from pathlib import Path

from pipeline.compose import render_section, load_tokens
from pipeline.stitch import stitch_sections

PROJECT = Path(__file__).parent
TOKENS_PATH = PROJECT / "design_tokens" / "premium-editorial.json"
FONTS_DIR = PROJECT / "fonts"
SAMPLE_REF = PROJECT / "tests" / "_fixtures" / "sample_ref.jpg"
OUT_DIR = PROJECT / "demo_output"

# 실제 Claude가 만들어줄 JSON과 동일한 형식의 사실적인 fake copy
FAKE_COPY = {
    "01_hero": {
        "headline_options": [
            "30년이 지나도 사랑받는 소파, B&B Italia Charles",
        ],
        "subheadline": "DUOMO가 정식 수입하는 정통 이탈리아 가구 — 14주 리드타임, 5년 A/S 포함",
        "urgency_badge": "2026 봄 시즌 한정",
        "cta_text": "전시장 방문 예약",
    },
    "02_pain": {
        "intro": "이런 고민, 익숙하지 않으세요?",
        "pain_points": [
            "백화점 가구는 어디나 비슷한 라인업, 진짜는 보이지 않습니다",
            "병행 수입은 가격은 매력적이지만, 진품·AS·보증서가 불안합니다",
            "디자인 잡지에서 본 그 브랜드, 한국 정식 수입사가 어디인지 모릅니다",
        ],
        "emotional_hook": "공간이 평범해지는 이유는, 진짜를 만나지 못해서입니다.",
    },
    "03_problem": {
        "hook": "안목이 부족한 게 아닙니다. 시장이 좁은 겁니다.",
        "reasons": [
            "국내 정식 수입사가 들여오는 라인업은 전체의 20%도 안 됩니다",
            "병행 수입은 진품 보증서·시리얼·AS·정식 패브릭이 보장되지 않습니다",
            "결국 정식 수입 큐레이터를 한 명 알고 있는 것이 답입니다",
        ],
        "reframe": "결국 검증된 큐레이션을 만나는 게 정답입니다.",
    },
    "04_story": {
        "before": "처음 인테리어 잡지에서 Cassina LC4를 본 게 8년 전이었습니다",
        "after": "지금 거실 창가, 그 셰이즈에 앉아 책을 읽습니다",
        "proof": "정식 수입 진품 + 평생 무상 컨설팅 + 5년 A/S로 가능했습니다.",
    },
    "05_solution": {
        "intro": "DUOMO PRESENTS",
        "product_name": "B&B Italia Charles",
        "one_liner": "미니멀리즘의 정의 — Antonio Citterio, 1997",
        "target_fit": "20평 이상 거실, 천장 높이 2.6m 이상의 공간에 가장 어울립니다.",
    },
    "06_how_it_works": {
        "intro": "이렇게 진행됩니다",
        "headline": "이렇게 진행됩니다",
        "subheadline": "전시장 방문 → 공간 컨설팅 → 이탈리아 공장 발주 → 전속 시공",
    },
    "07_social_proof": {
        "headline": "DUOMO를 선택한 이유",
        "intro": "DUOMO를 선택한 이유",
        "main_benefits": [
            "누적 시공 1,200건+ (2008~2026)",
            "재구매·소개 비율 68%",
            "평균 거래 연수 7.2년",
        ],
        "closing": "병행 수입과 비교해 가격은 비싸지만, 결국 정식 수입이 답이었습니다.",
    },
    "08_authority": {
        "intro": "DUOMO, since 2008",
        "headline": "18년 정식 수입 헤리티지",
        "subheadline": "B&B Italia · Cassina · Flos · Artemide · Foscarini 공식 한국 파트너",
        "cta_text": "회사 소개 보기",
    },
    "09_benefits": {
        "intro": "정식 수입이 포함하는 것",
        "headline": "정식 수입이 포함하는 것",
        "main_benefits": [
            "이탈리아 공장 직수입 — 정품 보증서 + 시리얼 넘버",
            "5년 무상 A/S (프레임·메커니즘 부품 포함)",
            "전속 설치팀 무료 시공 + 정기 점검",
            "패브릭·가죽·마감 옵션 풀 라인업 선택 가능",
            "공간 컨설팅 무료 (도면·3D 시뮬레이션 포함)",
        ],
        "closing": "단순 가구 구매가 아닌, 평생 소유 가치까지 포함합니다.",
    },
    "10_risk_removal": {
        "intro": "보증과 약속",
        "headline": "보증과 약속",
        "main_benefits": [
            "정식 수입 진품 보증서 + 시리얼 넘버",
            "5년 무상 A/S — 프레임·메커니즘 부품 포함",
            "전속 설치팀 평생 컨설팅",
        ],
        "closing": "단 한 가지라도 충족되지 않으면 전액 환불입니다.",
    },
    "11_comparison": {
        "intro": "선택의 본질",
        "headline": "5년 후 vs 30년 후",
        "main_benefits": [
            "어디서나 볼 수 있는, 5년 뒤 처분할 가구",
            "정식 수입 진품, 디자이너·연식 명확",
            "공간 컨설팅 → 발주 → 시공 → 사후 관리",
        ],
        "question": "5년 후를 위한 선택입니까, 30년 후를 위한 선택입니까?",
    },
    "12_target_filter": {
        "intro": "이런 분께 권합니다",
        "headline": "이런 분께 권합니다",
        "recommended": [
            "한 번 구매로 10년 이상 함께할 정통 디자인을 찾는 분",
            "정식 수입 진품·A/S·진행 투명성을 중시하는 분",
            "공간 설계 단계부터 큐레이션 받고 싶은 분",
        ],
        "closing": "리드타임 14주를 기다릴 수 있는 분께만 권해드립니다.",
    },
    "13_final_cta": {
        "headline_options": [
            "30년 뒤에도 후회 없을 선택, 직접 앉아보고 결정하세요.",
        ],
        "subheadline": "공식가 18,400,000원~ · DUOMO 정식 수입 패키지 (5년 A/S, 무료 시공, 컨설팅 포함)",
        "urgency_badge": "월 8건 한정 컨설팅",
        "cta_text": "전시장 방문 예약하기",
    },
}


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    tokens = load_tokens(TOKENS_PATH)

    section_paths: dict[str, Path] = {}
    print(f"Rendering 13 sections to {OUT_DIR}...")
    for section_key, cfg in tokens["sections"].items():
        copy_data = FAKE_COPY.get(section_key, {})
        ref_images = [SAMPLE_REF] if cfg["mode"] in ("image", "image_split") else []
        img = render_section(
            section_key=section_key,
            copy_data=copy_data,
            tokens=tokens,
            fonts_dir=FONTS_DIR,
            ref_images=ref_images,
        )
        out_path = OUT_DIR / f"{section_key}.png"
        img.save(out_path, "PNG")
        section_paths[section_key] = out_path
        print(f"  ok {section_key} ({cfg['mode']:11s}) {img.width}x{img.height}px")

    print(f"\nStitching final image...")
    final = OUT_DIR / "final.png"
    stitch_sections(section_paths, final)
    print(f"\nDone: {final}")
    print(f"Size: {final.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
