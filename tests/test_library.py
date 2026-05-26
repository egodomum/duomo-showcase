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


from pipeline.library import find_images_for_section


def test_match_priority_1_brand_and_model_exact():
    items = load_index(FIXTURE)
    brief = {"brand": "B&B Italia", "model": "Charles", "designer": "Antonio Citterio"}
    result = find_images_for_section(items, brief, "01_hero")
    assert len(result) == 1
    assert result[0]["id"] == "bbi-charles-living-001"


def test_match_priority_2_brand_only_when_model_missing():
    items = load_index(FIXTURE)
    brief = {"brand": "B&B Italia", "model": "Maxalto", "designer": "Antonio Citterio"}
    result = find_images_for_section(items, brief, "01_hero")
    assert len(result) >= 1
    assert all(r["brand"] == "B&B Italia" for r in result)


def test_match_priority_3_designer_when_brand_missing():
    items = load_index(FIXTURE)
    brief = {"brand": "Unknown", "model": "X", "designer": "Antonio Citterio"}
    result = find_images_for_section(items, brief, "01_hero")
    assert len(result) >= 1
    assert all(r["designer"] == "Antonio Citterio" for r in result)


def test_match_priority_4_section_fit_only_when_all_else_missing():
    items = load_index(FIXTURE)
    brief = {"brand": "Z", "model": "Z", "designer": "Z"}
    result = find_images_for_section(items, brief, "01_hero")
    assert len(result) >= 1
    assert all("01_hero" in r["section_fit"] for r in result)


def test_match_returns_empty_when_no_section_fit():
    items = load_index(FIXTURE)
    brief = {"brand": "Z", "model": "Z", "designer": "Z"}
    result = find_images_for_section(items, brief, "99_nonexistent")
    assert result == []


def test_match_respects_top_n_limit():
    items = load_index(FIXTURE)
    brief = {"brand": "Z", "model": "Z", "designer": "Z"}
    result = find_images_for_section(items, brief, "01_hero", top_n=1)
    assert len(result) == 1
