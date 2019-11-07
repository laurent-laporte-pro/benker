# coding: utf-8
from __future__ import division

import re

import pytest

from benker.colors.const import CSS_COLOR_NAMES
from benker.colors.css import css_name_to_rgba
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


def test_parse_css_name__invalid():
    with pytest.raises(ValueError, match=re.escape("Bleu profond")):
        parse_css_name("Bleu profond")


@pytest.mark.parametrize("text, rgb", sorted(CSS_COLOR_NAMES.items()))
def test_css_name_to_rgba(text, rgb):
    r, g, b, a = css_name_to_rgba(text)
    assert (r, g, b) == rgb
    assert a is None
    for p in [0, 0.25, 1, 1 / 3]:
        p_text = "{p:.2%}{text}".format(p=p, text=text)
        r, g, b, a = css_name_to_rgba(p_text)
        p = float("{p:.2f}".format(p=p * 100)) / 100
        assert round(r, 3) == round(rgb[0] * p, 3)
        assert round(g, 3) == round(rgb[1] * p, 3)
        assert round(b, 3) == round(rgb[2] * p, 3)
        assert a is None
