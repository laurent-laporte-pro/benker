# coding: utf-8
from benker.colors import RGBColor


def test_parse_rgba():
    # AliceBlue
    color = RGBColor.from_string("rgb(240, 248, 255)")
    assert color.r == 240
    assert color.g == 248
    assert color.b == 255
    assert color.a is None
    assert color.name is None
    assert str(color) == "rgb(240, 248, 255)"
