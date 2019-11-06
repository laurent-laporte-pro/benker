# coding: utf-8
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


@pytest.mark.parametrize(
    "text, expected",
    [
        ("#00000000", (0, 0, 0, 0)),
        ("#000000", (0, 0, 0, None)),
        ("#ffFFffFF", (0xFF, 0xFF, 0xFF, 1)),
        ("#FF8040C0", (0xFF, 0x80, 0x40, 0xC0 / 255.0)),
    ],
)
def test_parse_hex8(text, expected):
    r, g, b, a = parse_hex8(text)
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
    "text, expected",
    [
        ("#0000", (0, 0, 0, 0)),
        ("#000", (0, 0, 0, None)),
        ("#fFfF", (0xFF, 0xFF, 0xFF, 0xFF / 255.0)),
        ("#F84C", (0xFF, 0x88, 0x44, 0xCC / 255.0)),
    ],
)
def test_parse_hex4(text, expected):
    r, g, b, a = parse_hex4(text)
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
        ((0, 0, 0, None), "rgb(0%, 0%, 0%)"),
        ((0, 0, 0, 0), "rgba(0%, 0%, 0%, 0%)"),
        ((255, 255, 255, 1), "rgba(100%, 100%, 100%, 100%)"),
        ((255, 127.5, 63.75, 0.75), "rgba(100%, 50%, 25%, 75%)"),
        ((123, 234, 17, 1 / 3.0), "rgba(48.24%, 91.76%, 6.67%, 33.33%)"),
    ],
)
def test_format_rgba_percent(rgba, expected):
    text = format_rgba_percent(*rgba)
    assert text == expected
