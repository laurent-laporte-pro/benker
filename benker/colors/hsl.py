# coding: utf-8
"""
HSL Colors
==========

HSL/HSLA color parser, formatter and converter.
"""
from __future__ import division

import colorsys
import re

from benker.colors.const import HUE_SCALE
from benker.colors.const import RGB_SCALE
from benker.colors.misc import parse_num_value

_match_hsla = re.compile(r"^hsla?\(([^)]+)\)$", flags=re.I).match


def parse_hsla(text, hue_scale=HUE_SCALE):
    mo = _match_hsla(text)
    if mo:
        text = mo.group(1).strip()
        values = re.split(r"\s*,\s*", text)
        if len(values) == 4:
            h, s, l, a = values
        elif len(values) == 3:
            h, s, l = values
            a = None
        else:
            raise ValueError(text)
        try:
            k = hue_scale / HUE_SCALE
            h = parse_num_value(h, HUE_SCALE) * k
            s = parse_num_value(s, 1)
            l = parse_num_value(l, 1)
            if a:
                a = parse_num_value(a, 1)
                return h, s, l, a
            else:
                return h, s, l, None
        except ValueError:
            raise ValueError(text)
    else:
        raise ValueError(text)


def format_hsla(h, s, l, a=None, hue_scale=HUE_SCALE):
    k = hue_scale / HUE_SCALE
    h = round(h / k)
    s = round(s, 2)
    l = round(l, 2)
    if a is None:
        fmt = "hsl({h:g}, {s:g}, {l:g})"
    else:
        a = round(a, 2)
        fmt = "hsla({h:g}, {s:g}, {l:g}, {a:g})"
    return fmt.format(h=h, s=s, l=l, a=a)


def format_hsla_percent(h, s, l, a=None, hue_scale=HUE_SCALE):
    h = round(h / hue_scale * 100, 2)
    s = round(s * 100, 2)
    l = round(l * 100, 2)
    if a is None:
        fmt = "hsl({h:.5g}%, {s:.5g}%, {l:.5g}%)"
    else:
        a = round(a * 100, 2)
        fmt = "hsla({h:.5g}%, {s:.5g}%, {l:.5g}%, {a:.5g}%)"
    return fmt.format(h=h, s=s, l=l, a=a)


def hsla_to_rgba(h, s, l, a=None, hue_scale=HUE_SCALE, rgb_scale=RGB_SCALE):
    h = h / hue_scale
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    r = r * rgb_scale
    g = g * rgb_scale
    b = b * rgb_scale
    return r, g, b, a
