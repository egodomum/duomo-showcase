"""블록 공통 인터페이스. 각 블록은 spec(메타)과 render(data,tokens,refs)->HTML을 가진다."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable


@dataclass
class Field:
    """UI 입력 필드 정의."""
    key: str
    label: str
    kind: str  # "text" | "textarea" | "list" | "image"


@dataclass
class BlockSpec:
    """블록 메타데이터."""
    type: str
    label: str
    category: str  # "U" | "O" | "F" | "L"
    input_fields: list[Field] = field(default_factory=list)
    copy_schema: dict[str, Any] = field(default_factory=dict)


@runtime_checkable
class Block(Protocol):
    """블록 프로토콜."""
    spec: BlockSpec

    def render(self, data: dict[str, Any], tokens: dict[str, Any],
               refs: dict[str, str]) -> str:
        """HTML 조각(<section>...)을 반환한다."""
        ...


_ESCAPE = {"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"}


def escape_html(text: Any) -> str:
    """HTML 특수문자 이스케이프. None은 빈 문자열."""
    if text is None:
        return ""
    s = str(text)
    return "".join(_ESCAPE.get(ch, ch) for ch in s)


def nl2br(text: Any) -> str:
    """줄바꿈을 <br>로. 먼저 이스케이프."""
    return escape_html(text).replace("\n", "<br>")
