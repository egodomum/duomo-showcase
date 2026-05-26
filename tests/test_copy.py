"""pipeline.copy tests with mocked Anthropic client."""
import json
from unittest.mock import MagicMock

import pytest

from pipeline.copy import generate_copy, CopyError


def _mock_response(text):
    msg = MagicMock()
    msg.content = [MagicMock(text=text)]
    return msg


def test_generate_copy_returns_dict(tmp_path):
    """카피 JSON 응답을 파싱해 dict로 반환."""
    fake_json = json.dumps({
        "section_01_hero": {
            "headline_options": ["a", "b", "c"],
            "subheadline": "sub",
            "urgency_badge": "한정",
            "cta_text": "예약"
        }
    }, ensure_ascii=False)

    mock_client = MagicMock()
    mock_client.messages.create.return_value = _mock_response(fake_json)

    prompt_file = tmp_path / "03-copy.md"
    prompt_file.write_text("system prompt", encoding="utf-8")

    result = generate_copy(
        client=mock_client,
        brief={"brand": "B&B Italia"},
        research={"persona": "consumer"},
        system_prompt_path=prompt_file,
        model="claude-sonnet-4-5",
    )

    assert "section_01_hero" in result
    assert result["section_01_hero"]["cta_text"] == "예약"


def test_generate_copy_retries_on_invalid_json(tmp_path):
    """첫 응답이 JSON 아니면 'JSON only' 메시지로 1회 재요청."""
    bad = _mock_response("어 그러니까... section_01은...")
    good = _mock_response(json.dumps({"section_01_hero": {"cta_text": "예약"}},
                                     ensure_ascii=False))

    mock_client = MagicMock()
    mock_client.messages.create.side_effect = [bad, good]

    prompt_file = tmp_path / "03-copy.md"
    prompt_file.write_text("system prompt", encoding="utf-8")

    result = generate_copy(
        client=mock_client,
        brief={}, research={},
        system_prompt_path=prompt_file,
        model="claude-sonnet-4-5",
    )

    assert result["section_01_hero"]["cta_text"] == "예약"
    assert mock_client.messages.create.call_count == 2


def test_generate_copy_raises_after_second_failure(tmp_path):
    """두 번 다 JSON 파싱 실패하면 CopyError."""
    bad = _mock_response("not json")
    mock_client = MagicMock()
    mock_client.messages.create.side_effect = [bad, bad]

    prompt_file = tmp_path / "03-copy.md"
    prompt_file.write_text("system", encoding="utf-8")

    with pytest.raises(CopyError):
        generate_copy(
            client=mock_client,
            brief={}, research={},
            system_prompt_path=prompt_file,
            model="claude-sonnet-4-5",
        )


from pipeline.copy import generate_research, generate_design_direction


def test_generate_research(tmp_path):
    fake_json = json.dumps({"persona": {"primary": "consumer"}}, ensure_ascii=False)
    mock_client = MagicMock()
    mock_client.messages.create.return_value = _mock_response(fake_json)

    prompt_file = tmp_path / "02-research.md"
    prompt_file.write_text("research system", encoding="utf-8")

    result = generate_research(
        client=mock_client,
        brief={"brand": "B&B Italia"},
        system_prompt_path=prompt_file,
    )
    assert result["persona"]["primary"] == "consumer"


def test_generate_design_direction(tmp_path):
    fake_json = json.dumps({"style_preset": "premium-editorial"}, ensure_ascii=False)
    mock_client = MagicMock()
    mock_client.messages.create.return_value = _mock_response(fake_json)

    prompt_file = tmp_path / "04-design.md"
    prompt_file.write_text("design system", encoding="utf-8")

    result = generate_design_direction(
        client=mock_client,
        brief={},
        research={},
        system_prompt_path=prompt_file,
    )
    assert result["style_preset"] == "premium-editorial"
