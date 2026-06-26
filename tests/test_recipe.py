"""레시피 조작 헬퍼 테스트."""
from pipeline.recipe import new_recipe, add_block, remove_block, move_block


def test_new_recipe_has_meta_and_empty_blocks():
    r = new_recipe(brand="B&B Italia", product="Camaleonda")
    assert r["meta"]["brand"] == "B&B Italia"
    assert r["blocks"] == []


def test_add_block_appends():
    r = new_recipe(brand="X")
    add_block(r, "hero")
    assert r["blocks"][0]["type"] == "hero"
    assert r["blocks"][0]["data"] == {}


def test_remove_block_by_index():
    r = new_recipe(brand="X")
    add_block(r, "hero"); add_block(r, "intro")
    remove_block(r, 0)
    assert len(r["blocks"]) == 1
    assert r["blocks"][0]["type"] == "intro"


def test_move_block_up():
    r = new_recipe(brand="X")
    add_block(r, "hero"); add_block(r, "intro")
    move_block(r, 1, -1)
    assert r["blocks"][0]["type"] == "intro"


def test_move_block_bounds_safe():
    r = new_recipe(brand="X")
    add_block(r, "hero")
    move_block(r, 0, -1)
    assert r["blocks"][0]["type"] == "hero"
