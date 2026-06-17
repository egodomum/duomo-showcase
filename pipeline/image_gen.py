"""Gemini 2.5 Flash Image(Nano Banana) 무료 티어로 '텍스트 없는' 배경 이미지를 생성한다.

설계 원칙: Gemini는 배경(가구·공간)만 그린다. 한글 카피는 compose.py(PIL)가
오버레이하므로, 프롬프트에서 '이미지 안에 글자를 넣지 말 것'을 강하게 명시한다.

무료 티어: 하루 500장, 1024x1024, 카드 등록 불필요.
키 발급: https://aistudio.google.com/apikey  (Google 계정만 있으면 됨)
"""
from __future__ import annotations

import base64
import logging
import os
import time
from pathlib import Path
from typing import Any, Optional

import requests

log = logging.getLogger(__name__)

# 안정 모델명. preview 변형은 2026-01-15 종료됨.
DEFAULT_MODEL = os.getenv("GEMINI_IMAGE_MODEL", "gemini-2.5-flash-image")
API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"
TIMEOUT_S = 120

# 섹션 mode → 배경 장면 설명 (텍스트 없는 에디토리얼 인테리어)
_SCENE_BY_MODE = {
    "image": "a refined Korean apartment living room interior, the furniture as hero",
    "image_split": "a refined Korean apartment living room, calm and lived-in",
    "image_overlay_dark": "a refined Korean living room at twilight, low warm light",
}


class ImageGenError(Exception):
    """이미지 생성 실패."""


def build_background_prompt(
    brief: dict[str, Any],
    section_key: str,
    section_cfg: dict[str, Any],
) -> str:
    """브리프와 섹션 설정으로 '텍스트 없는' 배경 생성 프롬프트를 만든다."""
    brand = brief.get("brand", "premium designer furniture")
    model = brief.get("model", "")
    designer = brief.get("designer", "")
    subject = f"{brand} {model}".strip()

    bg_mode = section_cfg.get("background", "off-white")
    scene = _SCENE_BY_MODE.get(
        "image_overlay_dark" if bg_mode == "image_overlay_dark" else section_cfg.get("mode", "image"),
        _SCENE_BY_MODE["image"],
    )

    designer_note = f" designed by {designer}" if designer else ""

    return f"""Editorial interior photograph for a luxury furniture landing page.

SCENE: {scene}, featuring {subject}{designer_note}.

STYLE (mandatory):
- Magazine editorial photography — Wallpaper*, Architectural Digest, Casa Vogue tone
- Natural daylight, soft shadows, quiet-luxury mood, slightly desaturated warm grade
- Brand reference look: B&B Italia / Cassina / Minotti lookbooks
- Photorealistic, NOT illustration, NOT 3D render, NOT cartoon

COMPOSITION:
- Leave calm negative space (left or lower area) where text will be overlaid later
- {"Darker, moody twilight tones for a dark text overlay." if bg_mode == "image_overlay_dark" else "Bright, airy off-white tones."}

ABSOLUTELY NO TEXT:
- Do NOT render any letters, words, captions, logos, watermarks, or UI
- The image must be a clean photograph with zero typography

OUTPUT: a single 1024x1024 photograph, full bleed, no borders."""


def generate_background(
    prompt: str,
    out_path: Path,
    *,
    api_key: Optional[str] = None,
    model: str = DEFAULT_MODEL,
    retries: int = 3,
) -> Path:
    """프롬프트로 배경 이미지를 생성해 out_path에 저장하고 경로를 반환한다.

    Raises:
        ImageGenError: API 키 없음 / 응답에 이미지 없음 / 재시도 후에도 실패
    """
    api_key = api_key or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ImageGenError(
            "GEMINI_API_KEY가 없습니다. https://aistudio.google.com/apikey 에서 "
            "무료 키를 발급받아 .env에 넣으세요 (카드 등록 불필요)."
        )

    url = f"{API_BASE}/{model}:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseModalities": ["IMAGE"]},
    }

    last_err: Optional[Exception] = None
    for attempt in range(retries):
        try:
            resp = requests.post(url, json=payload, timeout=TIMEOUT_S)
            if resp.status_code == 429:
                # 무료 티어 분당 한도 초과 — 잠시 대기 후 재시도
                wait = 5 * (attempt + 1)
                log.warning("rate limited (429), waiting %ds", wait)
                time.sleep(wait)
                continue
            if resp.status_code != 200:
                raise ImageGenError(
                    f"Gemini API {resp.status_code}: {resp.text[:300]}"
                )
            data = resp.json()
            parts = (
                data.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [])
            )
            for part in parts:
                inline = part.get("inlineData") or part.get("inline_data")
                if inline and inline.get("data"):
                    out_path.parent.mkdir(parents=True, exist_ok=True)
                    out_path.write_bytes(base64.b64decode(inline["data"]))
                    log.info("background saved: %s", out_path)
                    return out_path
            raise ImageGenError(f"응답에 이미지 데이터 없음: {str(data)[:300]}")
        except requests.RequestException as e:
            last_err = e
            wait = 2 ** attempt
            log.warning("request failed (attempt %d): %s — retry in %ds",
                        attempt + 1, e, wait)
            time.sleep(wait)

    raise ImageGenError(f"{retries}회 시도 후 실패: {last_err}")
