from pathlib import Path
from PIL import Image

from pipeline.stitch import stitch_sections


def test_stitch_combines_sections(tmp_path):
    paths = {}
    for i, key in enumerate(["01_hero", "02_pain", "03_problem"]):
        p = tmp_path / f"{key}.png"
        Image.new("RGB", (1200, 200 + i * 100), "#FFFFFF").save(p)
        paths[key] = p

    out = tmp_path / "final.png"
    result = stitch_sections(paths, out)

    final = Image.open(result)
    assert final.width == 1200
    assert final.height == 200 + 300 + 400  # 200+300+400


def test_stitch_normalizes_width(tmp_path):
    paths = {"01_hero": tmp_path / "01.png"}
    Image.new("RGB", (1500, 800), "#FFF").save(paths["01_hero"])

    out = tmp_path / "final.png"
    result = stitch_sections(paths, out)

    final = Image.open(result)
    assert final.width == 1200
