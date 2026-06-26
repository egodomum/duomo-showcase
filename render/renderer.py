"""HTML → 1000px full_page PNG (Playwright 헤드리스 Chromium)."""
from __future__ import annotations

from pathlib import Path

from playwright.sync_api import sync_playwright


class RenderError(Exception):
    """렌더 실패."""


def render_html_to_png(html: str, out_path: Path, width: int = 1000) -> Path:
    """HTML 문자열을 width px 폭의 full_page PNG로 캡처한다.

    Raises:
        RenderError: Chromium 미설치 등 렌더 실패
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": width, "height": 1400})
            page.set_content(html, wait_until="networkidle")
            page.screenshot(path=str(out_path), full_page=True, type="png")
            browser.close()
    except Exception as e:  # noqa: BLE001
        raise RenderError(
            f"렌더 실패: {e}. Chromium 설치 필요 시 'python -m playwright install chromium'"
        ) from e
    return out_path
