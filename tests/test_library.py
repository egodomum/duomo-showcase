"""pipeline.library tests."""
from pathlib import Path

import pytest

from pipeline.library import load_index, LibraryIndexError

FIXTURE = Path(__file__).parent / "_fixtures" / "sample_index.json"


def test_load_index_returns_list_of_dicts():
    items = load_index(FIXTURE)
    assert isinstance(items, list)
    assert len(items) == 4
    assert items[0]["brand"] == "B&B Italia"


def test_load_index_validates_required_keys():
    """Missing 'id' should raise LibraryIndexError."""
    bad_file = FIXTURE.parent / "_bad_index.json"
    bad_file.write_text('[{"brand": "X"}]', encoding="utf-8")
    try:
        with pytest.raises(LibraryIndexError):
            load_index(bad_file)
    finally:
        bad_file.unlink()


def test_load_index_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        load_index(Path("/nonexistent.json"))
