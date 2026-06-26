"""블록 단위 쇼케이스 카피 생성 테스트 (모킹)."""
import json
from unittest.mock import MagicMock

from pipeline.copy import generate_block_copy, CopyError


def _mock(text):
    m = MagicMock()
    m.content = [MagicMock(text=text)]
    return m


def test_generate_block_copy_returns_dict(tmp_path):
    fake = json.dumps({"statement": "1966년 브리아자에서 시작되었습니다"},
                      ensure_ascii=False)
    client = MagicMock()
    client.messages.create.return_value = _mock(fake)
    prompt = tmp_path / "showcase-copy.md"
    prompt.write_text("system", encoding="utf-8")

    out = generate_block_copy(
        client=client, block_type="brand",
        copy_schema={"statement": "string"},
        meta={"brand": "B&B Italia"},
        system_prompt_path=prompt,
    )
    assert out["statement"].startswith("1966")


def test_generate_block_copy_retries_on_bad_json(tmp_path):
    bad = _mock("음 그러니까")
    good = _mock(json.dumps({"body": "둥근 소파입니다"}, ensure_ascii=False))
    client = MagicMock()
    client.messages.create.side_effect = [bad, good]
    prompt = tmp_path / "p.md"; prompt.write_text("s", encoding="utf-8")

    out = generate_block_copy(
        client=client, block_type="intro",
        copy_schema={"body": "string"}, meta={},
        system_prompt_path=prompt,
    )
    assert out["body"].startswith("둥근")
    assert client.messages.create.call_count == 2
