"""DUOMO 룩북 라이브러리 인덱스 로더와 검색 로직."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

REQUIRED_KEYS = {"id", "brand", "type", "section_fit"}


class LibraryIndexError(Exception):
    """라이브러리 인덱스 무결성 오류."""


def load_index(path: Path) -> list[dict[str, Any]]:
    """JSON 인덱스 파일을 로드하고 필수 키를 검증한다.

    Raises:
        FileNotFoundError: 파일 없음
        LibraryIndexError: JSON 파싱 실패 또는 필수 키 누락
    """
    if not path.exists():
        raise FileNotFoundError(f"Index not found: {path}")

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise LibraryIndexError(f"Invalid JSON in {path}: {e}") from e

    if not isinstance(data, list):
        raise LibraryIndexError(f"Index must be a JSON array, got {type(data).__name__}")

    for i, item in enumerate(data):
        missing = REQUIRED_KEYS - set(item.keys())
        if missing:
            raise LibraryIndexError(
                f"Index item #{i} missing required keys: {sorted(missing)}"
            )

    return data
