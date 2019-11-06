# coding: utf-8
import pytest

from benker.colors.rgb import parse_rgba
from benker.colors.rgb import format_rgba

@pytest.mark.parametrize(
    "text, expected",
    [
        ("rgba(0,0,0,0)", (0, 0, 0, 0)),
        ("rgb(0,0,0)", (0, 0, 0, None)),
        ("rgba(255, 255, 255, 1)", (255, 255, 255, 1)),
        ("rgba(255, 128, 64, 0.75)", (255, 128, 64, 0.75)),
        ("rgba(100%, 50%, 25%, 75%)", (255, 127.5, 63.75, 0.75)),
    ])
def test_parse_rgba(text, expected):
    r, g, b, a = parse_rgba(text)
    assert (r, g, b, a) == expected


@pytest.mark.parametrize(
    "rgba, expected",
    [
        ((0, 0, 0, None), "rgb(0, 0, 0)"),
        ((0, 0, 0, 0), "rgba(0, 0, 0, 0)"),
        ((255, 255, 255, 1), "rgba(255, 255, 255, 1)"),
        ((255, 127.5, 63.75, 0.75), "rgba(255, 128, 64, 0.75)"),
    ])
def test_format_rgba(rgba, expected):
    text = format_rgba(*rgba)
    assert text == expected
