# coding: utf-8
"""
CMYK Colors
===========

CMYK/CMYKA color parser, formatter and converter.
"""
from __future__ import division

import re

from benker.colors.const import CMYK_SCALE
from benker.colors.const import HUE_SCALE
from benker.colors.const import RGB_SCALE
from benker.colors.misc import parse_num_value
from benker.colors.rgb import rgb_to_hsl

_match_cmyka = re.compile(r"^cmyka?\(([^)]+)\)$", flags=re.I).match


def parse_cmyka(text, cmyk_scale=CMYK_SCALE):
    mo = _match_cmyka(text)
    if mo:
        coord = mo.group(1).strip()
        values = re.split(r"\s*,\s*", coord)
        if len(values) == 5:
            c, m, y, k, a = values
        elif len(values) == 4:
            c, m, y, k = values
            a = None
        else:
            raise ValueError(text)
        try:
            z = cmyk_scale / CMYK_SCALE
            c = parse_num_value(c, CMYK_SCALE) * z
            m = parse_num_value(m, CMYK_SCALE) * z
            y = parse_num_value(y, CMYK_SCALE) * z
            k = parse_num_value(k, CMYK_SCALE) * z
            if a:
                a = parse_num_value(a, 1)
                return c, m, y, k, a
            else:
                return c, m, y, k, None
        except ValueError:
            raise ValueError(text)
    else:
        raise ValueError(text)


def format_cmyka(c, m, y, k, a=None, cmyk_scale=CMYK_SCALE):
    z = cmyk_scale / CMYK_SCALE
    c = round(c / z)
    m = round(m / z)
    y = round(y / z)
    k = round(k / z)
    if a is None:
        fmt = "cmyk({c:g}, {m:g}, {y:g}, {k:g})"
    else:
        a = round(a, 2)
        fmt = "cmyka({c:g}, {m:g}, {y:g}, {k:g}, {a:g})"
    return fmt.format(c=c, m=m, y=y, k=k, a=a)


def format_cmyka_percent(c, m, y, k, a=None, cmyk_scale=CMYK_SCALE):
    c = round(c / cmyk_scale * 100, 2)
    m = round(m / cmyk_scale * 100, 2)
    y = round(y / cmyk_scale * 100, 2)
    k = round(k / cmyk_scale * 100, 2)
    if a is None:
        fmt = "cmyk({c:.5g}%, {m:.5g}%, {y:.5g}%, {k:.5g}%)"
    else:
        a = round(a * 100, 2)
        fmt = "cmyka({c:.5g}%, {m:.5g}%, {y:.5g}%, {k:.5g}%, {a:.5g}%)"
    return fmt.format(c=c, m=m, y=y, k=k, a=a)


def cmyk_to_rgb(c, m, y, k, cmyk_scale=CMYK_SCALE, rgb_scale=RGB_SCALE):
    r = rgb_scale * (1 - c / cmyk_scale) * (1 - k / cmyk_scale)
    g = rgb_scale * (1 - m / cmyk_scale) * (1 - k / cmyk_scale)
    b = rgb_scale * (1 - y / cmyk_scale) * (1 - k / cmyk_scale)
    return r, g, b


def cmyk_to_hsl(c, m, y, k, cmyk_scale=CMYK_SCALE, hue_scale=HUE_SCALE):
    r, g, b = cmyk_to_rgb(c, m, y, k, cmyk_scale=cmyk_scale)
    return rgb_to_hsl(r, g, b, hue_scale=hue_scale)
