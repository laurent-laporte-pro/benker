# coding: utf-8
from __future__ import division

import re

import pytest

from benker.colors.cmyk import cmyk_to_rgb
from benker.colors.cmyk import format_cmyk
from benker.colors.cmyk import format_cmyk_coord
from benker.colors.cmyk import format_cmyk_percent
from benker.colors.cmyk import format_cmyka
from benker.colors.cmyk import format_cmyka_coord
from benker.colors.cmyk import format_cmyka_percent
from benker.colors.cmyk import parse_cmyka


@pytest.mark.parametrize(
    "text, expected",
    [
        ("CMYK(100, 0, 0, 0)", (100, 0, 0, 0, None)),
        ("cmyk(0, 100, 0, 0)", (0, 100, 0, 0, None)),
        ("cmyk(0, 0, 100, 0)", (0, 0, 100, 0, None)),
        ("cmyk(0, 0, 0, 100)", (0, 0, 0, 100, None)),
        ("cmyka(0, 0, 0, 0, 1)", (0, 0, 0, 0, 1)),
        ("cmyk(50%, 50%, 50%, 50%)", (50, 50, 50, 50, None)),
    ],
)
def test_parse_cmyka(text, expected):
    c, m, y, k, a = parse_cmyka(text)
    assert (c, m, y, k, a) == expected


@pytest.mark.parametrize("text", ["cmyk(100, 0, 0)", "cmyk(100%)", "cmjn(100, 0, 0, 0)"])
def test_parse_cmyka__raises(text):
    with pytest.raises(ValueError, match=re.escape(text)):
        parse_cmyka(text)


@pytest.mark.parametrize(
    "text, expected",
    [
        ("cmyk(100, 75, 50, 25)", (1, 0.75, 0.5, 0.25, None)),
        ("cmyka(100, 75, 50, 25)", (1, 0.75, 0.5, 0.25, None)),
        ("cmyka(100, 75, 50, 25, 0.33)", (1, 0.75, 0.5, 0.25, 0.33)),
        ("cmyka(100%, 75%, 50%, 25%, 33%)", (1, 0.75, 0.5, 0.25, 0.33)),
    ],
)
def test_parse_cmyka__scale1(text, expected):
    c, m, y, k, a = parse_cmyka(text, cmyk_scale=1)
    if expected[4] is None:
        assert (c, m, y, k) == pytest.approx(expected[:4])
        assert a is None
    else:
        assert (c, m, y, k, a) == pytest.approx(expected)


@pytest.mark.parametrize(
    "cmyka, expected",
    [
        ((0, 0, 0, 0, None), "cmyk(0, 0, 0, 0)"),
        ((0, 0, 0, 0, 0), "cmyka(0, 0, 0, 0, 0)"),
        ((100, 75, 50, 25, 1 / 3), "cmyka(100, 75, 50, 25, 0.33)"),
    ],
)
def test_format_cmyka(cmyka, expected):
    text = format_cmyka(*cmyka)
    assert text == expected


@pytest.mark.parametrize(
    "cmyka, expected",
    [
        ((0, 0, 0, 0, None), "cmyk(0, 0, 0, 0)"),
        ((0, 0, 0, 0, 0), "cmyk(0, 0, 0, 0)"),
        ((100, 75, 50, 25, 1 / 3), "cmyk(100, 75, 50, 25)"),
    ],
)
def test_format_cmyk(cmyka, expected):
    text = format_cmyk(*cmyka)
    assert text == expected


@pytest.mark.parametrize(
    "cmyka, expected",
    [
        ((0, 0, 0, 0, None), "cmyk(0, 0, 0, 0)"),
        ((0, 0, 0, 0, 0), "cmyka(0, 0, 0, 0, 0)"),
        ((1, 0.75, 0.50, 0.25, 1 / 3), "cmyka(100, 75, 50, 25, 0.33)"),
    ],
)
def test_format_cmyka__scale1(cmyka, expected):
    text = format_cmyka(*cmyka, cmyk_scale=1)
    assert text == expected


@pytest.mark.parametrize(
    "cmyka, expected",
    [
        ((0, 0, 0, 0, None), "cmyk(0%, 0%, 0%, 0%)"),
        ((0, 0, 0, 0, 0), "cmyka(0%, 0%, 0%, 0%, 0%)"),
        ((100, 75, 50, 25, 1 / 3), "cmyka(100%, 75%, 50%, 25%, 33.33%)"),
    ],
)
def test_format_cmyka_percent(cmyka, expected):
    text = format_cmyka_percent(*cmyka)
    assert text == expected


@pytest.mark.parametrize(
    "cmyka, expected",
    [
        ((0, 0, 0, 0, None), "cmyk(0%, 0%, 0%, 0%)"),
        ((0, 0, 0, 0, 0), "cmyk(0%, 0%, 0%, 0%)"),
        ((100, 75, 50, 25, 1 / 3), "cmyk(100%, 75%, 50%, 25%)"),
    ],
)
def test_format_cmyk_percent(cmyka, expected):
    text = format_cmyk_percent(*cmyka)
    assert text == expected


@pytest.mark.parametrize(
    "cmyka, expected",
    [
        ((0, 0, 0, 0, None), "{0, 0, 0, 0}"),
        ((0, 0, 0, 0, 0), "{0, 0, 0, 0, 0}"),
        ((100, 75, 50, 25, 1 / 3), "{100, 75, 50, 25, 33.33}"),
    ],
)
def test_format_cmyka_coord(cmyka, expected):
    text = format_cmyka_coord(*cmyka)
    assert text == expected


@pytest.mark.parametrize(
    "cmyka, expected",
    [
        ((0, 0, 0, 0, None), "{0, 0, 0, 0}"),
        ((0, 0, 0, 0, 0), "{0, 0, 0, 0}"),
        ((100, 75, 50, 25, 1 / 3), "{100, 75, 50, 25}"),
    ],
)
def test_format_cmyk_coord(cmyka, expected):
    text = format_cmyk_coord(*cmyka)
    assert text == expected


@pytest.mark.parametrize(
    "cmyk, expected",
    [
        ((100, 0, 0, 0), (0, 255, 255)),
        ((0, 100, 0, 0), (255, 0, 255)),
        ((0, 0, 100, 0), (255, 255, 0)),
        ((0, 0, 0, 100), (0, 0, 0)),
        ((0, 0, 0, 0), (255, 255, 255)),
        ((50, 50, 50, 50), (63.75, 63.75, 63.75)),
    ],
)
def test_cmyk_to_rgb(cmyk, expected):
    r, g, b = cmyk_to_rgb(*cmyk)
    assert (r, g, b) == pytest.approx(expected)
