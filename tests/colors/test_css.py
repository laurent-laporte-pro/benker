# coding: utf-8
from __future__ import division

import re

import pytest

from benker.colors.const import CSS_COLOR_NAMES
from benker.colors.css import css_name_to_cmyk
from benker.colors.css import css_name_to_hsl
from benker.colors.css import css_name_to_rgb
from benker.colors.css import parse_css_name


@pytest.mark.parametrize("text", sorted(CSS_COLOR_NAMES))
def test_parse_css_name(text):
    color_name, percent = parse_css_name(text)
    assert color_name == text
    assert percent == 1
    for p in [0, 0.25, 1, 1 / 3]:
        p_text = "{p:.2%}{text}".format(p=p, text=text)
        color_name, percent = parse_css_name(p_text)
        assert color_name == text
        assert round(percent, 3) == round(p, 3)


@pytest.mark.parametrize("text", ["rainbow"])
def test_parse_css_name__raises(text):
    with pytest.raises(ValueError, match=re.escape(text)):
        parse_css_name(text)


def test_parse_css_name__invalid():
    with pytest.raises(ValueError, match=re.escape("Bleu profond")):
        parse_css_name("Bleu profond")


@pytest.mark.parametrize("text, rgb", sorted(CSS_COLOR_NAMES.items()))
def test_css_name_to_rgb(text, rgb):
    r, g, b = css_name_to_rgb(text)
    assert (r, g, b) == rgb
    for p in [0, 0.25, 1, 1 / 3]:
        p_text = "{p:.2%}{text}".format(p=p, text=text)
        r, g, b = css_name_to_rgb(p_text)
        p = float("{p:.2f}".format(p=p * 100)) / 100
        assert round(r, 3) == round(rgb[0] * p, 3)
        assert round(g, 3) == round(rgb[1] * p, 3)
        assert round(b, 3) == round(rgb[2] * p, 3)


@pytest.mark.parametrize(
    "text, hsl",
    [
        ("red", (0, 1, 0.5)),
        ("yellow", (60, 1, 0.5)),
        ("lime", (120, 1, 0.5)),
        ("cyan", (180, 1, 0.5)),
        ("blue", (240, 1, 0.5)),
        ("magenta", (300, 1, 0.5)),
        ("white", (0, 0, 1)),
        ("black", (0, 0, 0)),
    ],
)
def test_css_name_to_hsl(text, hsl):
    h, s, l = css_name_to_hsl(text)
    assert (h, s, l) == hsl


@pytest.mark.parametrize(
    "text, cmyk",
    [
        ("red", (0, 100, 100, 0)),
        ("yellow", (0, 0, 100, 0)),
        ("lime", (100, 0, 100, 0)),
        ("cyan", (100, 0, 0, 0)),
        ("blue", (100, 100, 0, 0)),
        ("magenta", (0, 100, 0, 0)),
        ("white", (0, 0, 0, 0)),
        ("black", (0, 0, 0, 100)),
    ],
)
def test_css_name_to_cmyk(text, cmyk):
    c, m, y, k = css_name_to_cmyk(text)
    assert (c, m, y, k) == cmyk
