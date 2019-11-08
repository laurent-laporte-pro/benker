# coding: utf-8
from __future__ import division

import re

import pytest

from benker.colors.hsl import format_hsl
from benker.colors.hsl import format_hsl_percent
from benker.colors.hsl import format_hsla
from benker.colors.hsl import format_hsla_percent
from benker.colors.hsl import hsl_to_rgb
from benker.colors.hsl import parse_hsla


@pytest.mark.parametrize(
    "text, expected",
    [
        ("hsl(0, 100%, 50%)", (0, 1, 0.5, None)),  # red
        ("hsl(120, 100%, 50%)", (120, 1, 0.5, None)),  # lime
        ("hsl(120, 100%, 25%)", (120, 1, 0.25, None)),  # dark green
        ("hsl(120, 100%, 75%)", (120, 1, 0.75, None)),  # light green
        ("hsl(120, 75%, 75%)", (120, 0.75, 0.75, None)),  # pastel green
        ("hsla(0,0,0,0)", (0, 0, 0, 0)),
        ("hsl(0,0,0)", (0, 0, 0, None)),
        ("hsla(360, 1, 1, 1)", (360, 1, 1, 1)),
        ("hsla(360, .5, .25, 0.75)", (360, 0.5, 0.25, 0.75)),
        ("hsla(100%, 50%, 25%, 75%)", (360, 0.5, 0.25, 0.75)),
    ],
)
def test_parse_hsla(text, expected):
    h, s, l, a = parse_hsla(text)
    assert (h, s, l, a) == expected


@pytest.mark.parametrize("text", ["hsl(100, 0)", "hsl(100%)", "hls(100, 0, 0)"])
def test_parse_hsla__raises(text):
    with pytest.raises(ValueError, match=re.escape(text)):
        parse_hsla(text)


@pytest.mark.parametrize(
    "text, expected",
    [
        ("hsl(0, 100%, 50%)", (0, 1, 0.5, None)),  # red
        ("hsl(120, 100%, 50%)", (1 / 3, 1, 0.5, None)),  # lime
        ("hsl(120, 100%, 25%)", (1 / 3, 1, 0.25, None)),  # dark green
        ("hsl(120, 100%, 75%)", (1 / 3, 1, 0.75, None)),  # light green
        ("hsl(120, 75%, 75%)", (1 / 3, 0.75, 0.75, None)),  # pastel green
        ("hsla(0,0,0,0)", (0, 0, 0, 0)),
        ("hsl(0,0,0)", (0, 0, 0, None)),
        ("hsla(360, 1, 1, 1)", (1, 1, 1, 1)),
        ("hsla(360, .5, .25, 0.75)", (1, 0.5, 0.25, 0.75)),
        ("hsla(100%, 50%, 25%, 75%)", (1, 0.5, 0.25, 0.75)),
    ],
)
def test_parse_hsla__scale1(text, expected):
    h, s, l, a = parse_hsla(text, hue_scale=1)
    if expected[3] is None:
        assert (h, s, l) == pytest.approx(expected[:3])
        assert a is None
    else:
        assert (h, s, l, a) == pytest.approx(expected)


@pytest.mark.parametrize(
    "hsla, expected",
    [
        ((0, 0, 0, None), "hsl(0, 0, 0)"),
        ((0, 0, 0, 0), "hsla(0, 0, 0, 0)"),
        ((120, 1, 1, 1), "hsla(120, 1, 1, 1)"),
        ((120, 0.5, 0.25, 0.75), "hsla(120, 0.5, 0.25, 0.75)"),
    ],
)
def test_format_hsla(hsla, expected):
    text = format_hsla(*hsla)
    assert text == expected


@pytest.mark.parametrize(
    "hsla, expected",
    [
        ((0, 0, 0, None), "hsl(0, 0, 0)"),
        ((0, 0, 0, 0), "hsl(0, 0, 0)"),
        ((120, 1, 1, 1), "hsl(120, 1, 1)"),
        ((120, 0.5, 0.25, 0.75), "hsl(120, 0.5, 0.25)"),
    ],
)
def test_format_hsl(hsla, expected):
    text = format_hsl(*hsla)
    assert text == expected


@pytest.mark.parametrize(
    "hsla, expected",
    [
        ((0, 0, 0, None), "hsl(0, 0, 0)"),
        ((0, 0, 0, 0), "hsla(0, 0, 0, 0)"),
        ((1 / 3, 1, 1, 1), "hsla(120, 1, 1, 1)"),
        ((1 / 3, 0.5, 0.25, 0.75), "hsla(120, 0.5, 0.25, 0.75)"),
    ],
)
def test_format_hsla__scale1(hsla, expected):
    text = format_hsla(*hsla, hue_scale=1)
    assert text == expected


@pytest.mark.parametrize(
    "hsla, expected",
    [
        ((0, 0, 0, None), "hsl(0%, 0%, 0%)"),
        ((0, 0, 0, 0), "hsla(0%, 0%, 0%, 0%)"),
        ((120, 1, 1, 1), "hsla(33.33%, 100%, 100%, 100%)"),
        ((120, 0.5, 0.25, 0.75), "hsla(33.33%, 50%, 25%, 75%)"),
    ],
)
def test_format_hsla_percent(hsla, expected):
    text = format_hsla_percent(*hsla)
    assert text == expected


@pytest.mark.parametrize(
    "hsla, expected",
    [
        ((0, 0, 0, None), "hsl(0%, 0%, 0%)"),
        ((0, 0, 0, 0), "hsl(0%, 0%, 0%)"),
        ((120, 1, 1, 1), "hsl(33.33%, 100%, 100%)"),
        ((120, 0.5, 0.25, 0.75), "hsl(33.33%, 50%, 25%)"),
    ],
)
def test_format_hsl_percent(hsla, expected):
    text = format_hsl_percent(*hsla)
    assert text == expected


@pytest.mark.parametrize(
    "hsl, expected",
    [
        ((0, 1, 0.5), (255, 0, 0)),  # red
        ((120, 1, 0.5), (0, 255, 0)),  # lime
        ((120, 1, 0.25), (0, 127.5, 0)),  # dark green
        ((120, 1, 0.75), (127.5, 255, 127.5)),  # light green
        ((120, 0.75, 0.75), (143.4375, 239.0625, 143.4375)),  # pastel green
    ],
)
def test_hsl_to_rgb(hsl, expected):
    r, g, b = hsl_to_rgb(*hsl)
    assert (r, g, b) == pytest.approx(expected)
