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


def find_images_for_section(
    index: list[dict[str, Any]],
    brief: dict[str, Any],
    section_key: str,
    top_n: int = 5,
) -> list[dict[str, Any]]:
    """4단계 우선순위로 섹션에 적합한 이미지를 찾는다.

    1순위: brand + model 정확 매칭
    2순위: brand만 매칭
    3순위: designer 매칭
    4순위: section_fit만 매칭

    Args:
        index: load_index()로 로드한 라이브러리 인덱스
        brief: brand, model, designer 키를 가진 입력
        section_key: 예) "01_hero"
        top_n: 최대 반환 개수

    Returns:
        매칭된 이미지 메타데이터 리스트. 매칭 없으면 빈 리스트.
    """
    base = [i for i in index if section_key in i.get("section_fit", [])]
    if not base:
        return []

    brand = brief.get("brand")
    model = brief.get("model")
    designer = brief.get("designer")

    if brand and model:
        tier1 = [i for i in base if i.get("brand") == brand and i.get("model") == model]
        if tier1:
            return tier1[:top_n]

    if brand:
        tier2 = [i for i in base if i.get("brand") == brand]
        if tier2:
            return tier2[:top_n]

    if designer:
        tier3 = [i for i in base if i.get("designer") == designer]
        if tier3:
            return tier3[:top_n]

    return base[:top_n]


class LibraryRepository:
    """Drive에서 인덱스를 로드하고 메모리 캐시한다."""

    def __init__(self, drive, index_drive_id: str, cache_dir: Path):
        self.drive = drive
        self.index_drive_id = index_drive_id
        self.cache_dir = cache_dir
        self._items: Optional[list[dict[str, Any]]] = None

    def list_all(self) -> list[dict[str, Any]]:
        """인덱스를 반환한다. 캐시되어 있지 않으면 Drive에서 가져옴."""
        if self._items is None:
            local_index = self.drive.download(self.index_drive_id, mime_suffix=".json")
            self._items = load_index(local_index)
        return self._items

    def refresh(self) -> None:
        """다음 list_all() 호출 시 Drive에서 다시 가져오도록 캐시 무효화."""
        self._items = None

    def find_for_section(self, brief: dict, section_key: str, top_n: int = 5
                         ) -> list[dict[str, Any]]:
        return find_images_for_section(self.list_all(), brief, section_key, top_n)
