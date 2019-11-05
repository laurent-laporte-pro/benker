# coding: utf-8
from benker.colors import RGBColor


def test_parse():
    assert 0


def test_parse_rgba():
    # AliceBlue
    color = RGBColor.from_string("rgb(240, 248, 255)")
    assert color.r == 240
    assert color.g == 248
    assert color.b == 255
    assert color.a is None
    assert color.name is None
    assert str(color) == "rgb(240, 248, 255)"


def test_parse_hsla():
    assert 0


def test_parse_cmyk():
    assert 0


def test_parse_hex8():
    assert 0


def test_parse_hex4():
    assert 0


def test_parse_name():
    assert 0


def test_parse_percent_name():
    assert 0


def test_parse_other_name():
    assert 0
