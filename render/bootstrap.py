"""런타임 Chromium 보장 — Streamlit Community Cloud 등 브라우저 바이너리가 없는 환경 대응.

Streamlit Cloud는 배포 후 터미널 접근이 없어 `playwright install`을 미리 못 돌린다.
앱 첫 부팅 시 1회 설치한다(이미 있으면 playwright가 빠르게 no-op). 로컬에선 즉시 통과.
"""
from __future__ import annotations

import logging
import subprocess
import sys

log = logging.getLogger(__name__)

_ensured = False


def ensure_chromium() -> None:
    """Chromium 바이너리를 보장한다. 프로세스당 1회만 시도(멱등)."""
    global _ensured
    if _ensured:
        return
    try:
        subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            check=False, timeout=600,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
    except Exception as e:  # noqa: BLE001 — 설치 실패해도 앱은 띄운다
        log.warning("playwright chromium 설치 시도 실패(무시): %s", e)
    _ensured = True
