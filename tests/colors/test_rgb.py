# coding: utf-8
from __future__ import division

import pytest

from benker.colors.rgb import format_hex3
from benker.colors.rgb import format_hex3_upper
from benker.colors.rgb import format_hex4
from benker.colors.rgb import format_hex4_upper
from benker.colors.rgb import format_hex6
from benker.colors.rgb import format_hex6_upper
from benker.colors.rgb import format_hex8
from benker.colors.rgb import format_hex8_upper
from benker.colors.rgb import format_rgba
from benker.colors.rgb import format_rgba_percent
from benker.colors.rgb import parse_hex4
from benker.colors.rgb import parse_hex8
from benker.colors.rgb import parse_rgba
from benker.colors.rgb import rgba_to_hsla


@pytest.mark.parametrize(
    "text, expected",
    [
        ("#00000000", (0, 0, 0, 0)),
        ("#000000", (0, 0, 0, None)),
        ("#ffFFffFF", (0xFF, 0xFF, 0xFF, 1)),
        ("#FF8040C0", (0xFF, 0x80, 0x40, 0xC0 / 255)),
    ],
)
def test_parse_hex8(text, expected):
    r, g, b, a = parse_hex8(text)
    assert (r, g, b, a) == expected


@pytest.mark.parametrize(
    "text, expected",
    [
        ("#00000000", (0, 0, 0, 0)),
        ("#000000", (0, 0, 0, None)),
        ("#ffFFffFF", (1, 1, 1, 1)),
        ("#FF8040C0", (1, 0x80 / 255, 0x40 / 255, 0xC0 / 255)),
    ],
)
def test_parse_hex8__scale1(text, expected):
    r, g, b, a = parse_hex8(text, rgb_scale=1)
    assert (r, g, b, a) == expected


def test_parse_hex8__range():
    for i in range(256):
        text = "#{:02x}0000".format(i)
        r, g, b, a = parse_hex8(text)
        assert (r, g, b, a) == (i, 0, 0, None)
        text = "#00{:02x}00".format(i)
        r, g, b, a = parse_hex8(text)
        assert (r, g, b, a) == (0, i, 0, None)
        text = "#0000{:02x}".format(i)
        r, g, b, a = parse_hex8(text)
        assert (r, g, b, a) == (0, 0, i, None)


@pytest.mark.parametrize(
    "rgba, expected",
    [
        ((0, 0, 0, None), "#000000"),
        ((0, 0, 0, 0), "#00000000"),
        ((255, 255, 255, 1), "#ffffffff"),
        ((255, 127.5, 63.75, 0.75), "#ff8040bf"),
        ((123, 234, 17, 1 / 3.0), "#7bea1155"),
    ],
)
def test_format_hex8(rgba, expected):
    text = format_hex8(*rgba)
    assert text == expected
    assert len(text) == 1 + 8 or len(text) == 1 + 6
    text = format_hex8_upper(*rgba)
    assert text == expected.upper()
    assert len(text) == 1 + 8 or len(text) == 1 + 6
    text = format_hex6(*rgba)
    assert text == expected[:7]
    assert len(text) == 1 + 6
    text = format_hex6_upper(*rgba)
    assert text == expected[:7].upper()
    assert len(text) == 1 + 6


@pytest.mark.parametrize(
    "rgba, expected",
    [
        ((0, 0, 0, 0), "#00000000"),
        ((0, 0, 0, None), "#000000"),
        ((1, 1, 1, 1), "#ffffffff"),
        ((1, 0x80 / 255, 0x40 / 255, 0xC0 / 255), "#ff8040c0"),
    ],
)
def test_format_hex8__scale1(rgba, expected):
    text = format_hex8(*rgba, rgb_scale=1)
    assert text == expected


@pytest.mark.parametrize(
    "text, expected",
    [
        ("#0000", (0, 0, 0, 0)),
        ("#000", (0, 0, 0, None)),
        ("#fFfF", (0xFF, 0xFF, 0xFF, 0xFF / 255)),
        ("#F84C", (0xFF, 0x88, 0x44, 0xCC / 255)),
    ],
)
def test_parse_hex4(text, expected):
    r, g, b, a = parse_hex4(text)
    assert (r, g, b, a) == expected


@pytest.mark.parametrize(
    "text, expected",
    [
        ("#0000", (0, 0, 0, 0)),
        ("#000", (0, 0, 0, None)),
        ("#fFfF", (0xFF / 255, 0xFF / 255, 0xFF / 255, 0xFF / 255)),
        ("#F84C", (0xFF / 255, 0x88 / 255, 0x44 / 255, 0xCC / 255)),
    ],
)
def test_parse_hex4__scale1(text, expected):
    r, g, b, a = parse_hex4(text, rgb_scale=1)
    assert (r, g, b, a) == expected


@pytest.mark.parametrize(
    "text, expected",
    [
        ("#0000", (0, 0, 0, 0)),
        ("#000", (0, 0, 0, None)),
        ("#fFfF", (0xFF / 255, 0xFF / 255, 0xFF / 255, 0xFF / 255)),
        ("#F84C", (0xFF / 255, 0x88 / 255, 0x44 / 255, 0xCC / 255)),
    ],
)
def test_parse_hex4__scale1(text, expected):
    r, g, b, a = parse_hex4(text, rgb_scale=1)
    assert (r, g, b, a) == expected


@pytest.mark.parametrize(
    "rgba, expected",
    [
        ((0, 0, 0, None), "#000"),
        ((0, 0, 0, 0), "#0000"),
        ((0xFF, 0xFF, 0xFF, 1), "#ffff"),
        ((0xFF, 0x88, 0x44, 0.75), "#f84b"),
        ((123, 234, 17, 1 / 3.0), "#7e15"),
    ],
)
def test_format_hex4(rgba, expected):
    text = format_hex4(*rgba)
    assert text == expected
    assert len(text) == 1 + 4 or len(text) == 1 + 3
    text = format_hex4_upper(*rgba)
    assert text == expected.upper()
    assert len(text) == 1 + 4 or len(text) == 1 + 3
    text = format_hex3(*rgba)
    assert text == expected[:4]
    assert len(text) == 1 + 3
    text = format_hex3_upper(*rgba)
    assert text == expected[:4].upper()
    assert len(text) == 1 + 3


@pytest.mark.parametrize(
    "rgba, expected",
    [
        ((0, 0, 0, 0), "#0000"),
        ((0, 0, 0, None), "#000"),
        ((1, 1, 1, 1), "#ffff"),
        ((1, 0x88 / 255, 0x44 / 255, 0xCC / 255), "#f84c"),
    ],
)
def test_format_hex4__scale1(rgba, expected):
    text = format_hex4(*rgba, rgb_scale=1)
    assert text == expected


@pytest.mark.parametrize(
    "text, expected",
    [
        ("rgba(0,0,0,0)", (0, 0, 0, 0)),
        ("rgb(0,0,0)", (0, 0, 0, None)),
        ("rgba(255, 255, 255, 1)", (255, 255, 255, 1)),
        ("rgba(255, 128, 64, 0.75)", (255, 128, 64, 0.75)),
        ("rgba(100%, 50%, 25%, 75%)", (255, 127.5, 63.75, 0.75)),
    ],
)
def test_parse_rgba(text, expected):
    r, g, b, a = parse_rgba(text)
    assert (r, g, b, a) == expected


@pytest.mark.parametrize(
    "text, expected",
    [
        ("rgba(0,0,0,0)", (0, 0, 0, 0)),
        ("rgb(0,0,0)", (0, 0, 0, None)),
        ("rgba(255, 255, 255, 1)", (1, 1, 1, 1)),
        ("rgba(255, 128, 64, 0.75)", (1, 128 / 255, 64 / 255, 0.75)),
        ("rgba(100%, 50%, 25%, 75%)", (1, 0.5, 0.25, 0.75)),
    ],
)
def test_parse_rgba__scale1(text, expected):
    r, g, b, a = parse_rgba(text, rgb_scale=1)
    assert (r, g, b, a) == expected


@pytest.mark.parametrize(
    "rgba, expected",
    [
        ((0, 0, 0, None), "rgb(0, 0, 0)"),
        ((0, 0, 0, 0), "rgba(0, 0, 0, 0)"),
        ((255, 255, 255, 1), "rgba(255, 255, 255, 1)"),
        ((255, 127.5, 63.75, 0.75), "rgba(255, 128, 64, 0.75)"),
        ((123, 234, 17, 1 / 3.0), "rgba(123, 234, 17, 0.333333)"),
    ],
)
def test_format_rgba(rgba, expected):
    text = format_rgba(*rgba)
    assert text == expected


@pytest.mark.parametrize(
    "rgba, expected",
    [
        ((0, 0, 0, None), "rgb(0, 0, 0)"),
        ((0, 0, 0, 0), "rgba(0, 0, 0, 0)"),
        ((1, 1, 1, 1), "rgba(255, 255, 255, 1)"),
        ((1, 0.5, 0.25, 0.75), "rgba(255, 128, 64, 0.75)"),
        ((123 / 255, 234 / 255, 17 / 255, 1 / 3), "rgba(123, 234, 17, 0.333333)"),
    ],
)
def test_format_rgba__scale1(rgba, expected):
    text = format_rgba(*rgba, rgb_scale=1)
    assert text == expected


@pytest.mark.parametrize(
    "rgba, expected",
    [
        ((0, 0, 0, None), "rgb(0%, 0%, 0%)"),
        ((0, 0, 0, 0), "rgba(0%, 0%, 0%, 0%)"),
        ((255, 255, 255, 1), "rgba(100%, 100%, 100%, 100%)"),
        ((255, 127.5, 63.75, 0.75), "rgba(100%, 50%, 25%, 75%)"),
        ((123, 234, 17, 1 / 3), "rgba(48.24%, 91.76%, 6.67%, 33.33%)"),
    ],
)
def test_format_rgba_percent(rgba, expected):
    text = format_rgba_percent(*rgba)
    assert text == expected


@pytest.mark.parametrize(
    "rgb, expected",
    [
        ((255, 0, 0), (0, 1, 0.5)),  # red
        ((0, 255, 0), (120, 1, 0.5)),  # lime
        ((0, 127.5, 0), (120, 1, 0.25)),  # dark green
        ((127.5, 255, 127.5), (120, 1, 0.75)),  # light green
        ((143.4375, 239.0625, 143.4375), (120, 0.75, 0.75)),  # pastel green
    ],
)
def test_rgba_to_hsla(rgb, expected):
    h, s, l, a = rgba_to_hsla(*rgb)
    assert (h, s, l) == pytest.approx(expected)
    assert a is None
