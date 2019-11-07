# coding: utf-8
"""
RGB Colors
==========

RGB/RGBA color parser, formatter and converter.
"""
from __future__ import division

import colorsys
import re

from benker.colors.const import CMYK_SCALE
from benker.colors.const import HUE_SCALE
from benker.colors.const import RGB_SCALE
from benker.colors.misc import parse_num_value

_match_hex8 = re.compile(
    r"^#(?P<r>[0-9a-f]{2})(?P<g>[0-9a-f]{2})(?P<b>[0-9a-f]{2})(?P<a>[0-9a-f]{2})?$", flags=re.I
).match


def parse_hex8(text, rgb_scale=RGB_SCALE):
    mo = _match_hex8(text)
    if mo:
        r, g, b, a = mo.group("r", "g", "b", "a")
        z = rgb_scale / RGB_SCALE
        r = int(r, 16) * z
        g = int(g, 16) * z
        b = int(b, 16) * z
        if a:
            a = int(a, 16) / RGB_SCALE
            return r, g, b, a
        else:
            return r, g, b, None
    else:
        raise ValueError(text)


def format_hex8(r, g, b, a=None, rgb_scale=RGB_SCALE):
    z = rgb_scale / RGB_SCALE
    r = int(round(r / z))
    g = int(round(g / z))
    b = int(round(b / z))
    if a is None:
        fmt = "#{r:02x}{g:02x}{b:02x}"
    else:
        a = int(round(a * RGB_SCALE))
        fmt = "#{r:02x}{g:02x}{b:02x}{a:02x}"
    return fmt.format(r=r, g=g, b=b, a=a)


def format_hex8_upper(r, g, b, a=None, rgb_scale=RGB_SCALE):
    return format_hex8(r, g, b, a=a, rgb_scale=rgb_scale).upper()


def format_hex6(r, g, b, a=None, rgb_scale=RGB_SCALE):
    return format_hex8(r, g, b, a=a, rgb_scale=rgb_scale)[:7]


def format_hex6_upper(r, g, b, a=None, rgb_scale=RGB_SCALE):
    return format_hex8(r, g, b, a=a, rgb_scale=rgb_scale)[:7].upper()


_match_hex4 = re.compile(r"^#(?P<r>[0-9a-f])(?P<g>[0-9a-f])(?P<b>[0-9a-f])(?P<a>[0-9a-f])?$", flags=re.I).match


def parse_hex4(text, rgb_scale=RGB_SCALE):
    mo = _match_hex4(text)
    if mo:
        r, g, b, a = mo.group("r", "g", "b", "a")
        z = rgb_scale / RGB_SCALE
        r = int(r * 2, 16) * z
        g = int(g * 2, 16) * z
        b = int(b * 2, 16) * z
        if a:
            a = int(a * 2, 16) / RGB_SCALE
            return r, g, b, a
        else:
            return r, g, b, None
    else:
        raise ValueError(text)


def format_hex4(r, g, b, a=None, rgb_scale=RGB_SCALE):
    z = rgb_scale / RGB_SCALE
    r = int(round(r / z / 17))
    g = int(round(g / z / 17))
    b = int(round(b / z / 17))
    if a is None:
        fmt = "#{r:01x}{g:01x}{b:01x}"
    else:
        a = int(round(a * RGB_SCALE / 17))
        fmt = "#{r:01x}{g:01x}{b:01x}{a:01x}"
    return fmt.format(r=r, g=g, b=b, a=a)


def format_hex4_upper(r, g, b, a=None, rgb_scale=RGB_SCALE):
    return format_hex4(r, g, b, a=a, rgb_scale=rgb_scale).upper()


def format_hex3(r, g, b, a=None, rgb_scale=RGB_SCALE):
    return format_hex4(r, g, b, a=a, rgb_scale=rgb_scale)[:4]


def format_hex3_upper(r, g, b, a=None, rgb_scale=RGB_SCALE):
    return format_hex4(r, g, b, a=a, rgb_scale=rgb_scale)[:4].upper()


_match_rgba = re.compile(r"^rgba?\(([^)]+)\)$", flags=re.I).match


def parse_rgba(text, rgb_scale=RGB_SCALE):
    mo = _match_rgba(text)
    if mo:
        coord = mo.group(1).strip()
        values = re.split(r"\s*,\s*", coord)
        if len(values) == 4:
            r, g, b, a = values
        elif len(values) == 3:
            r, g, b = values
            a = None
        else:
            raise ValueError(text)
        try:
            z = rgb_scale / RGB_SCALE
            r = parse_num_value(r, RGB_SCALE) * z
            g = parse_num_value(g, RGB_SCALE) * z
            b = parse_num_value(b, RGB_SCALE) * z
            if a:
                a = parse_num_value(a, 1)
                return r, g, b, a
            else:
                return r, g, b, None
        except ValueError:
            raise ValueError(text)
    else:
        raise ValueError(text)


def format_rgba(r, g, b, a=None, rgb_scale=RGB_SCALE):
    z = rgb_scale / RGB_SCALE
    r = round(r / z)
    g = round(g / z)
    b = round(b / z)
    if a is None:
        fmt = "rgb({r:g}, {g:g}, {b:g})"
    else:
        fmt = "rgba({r:g}, {g:g}, {b:g}, {a:g})"
    return fmt.format(r=r, g=g, b=b, a=a)


def format_rgba_percent(r, g, b, a=None, rgb_scale=RGB_SCALE):
    r = round(r / rgb_scale * 100, 2)
    g = round(g / rgb_scale * 100, 2)
    b = round(b / rgb_scale * 100, 2)
    if a is None:
        fmt = "rgb({r:.5g}%, {g:.5g}%, {b:.5g}%)"
    else:
        a = round(a * 100, 2)
        fmt = "rgba({r:.5g}%, {g:.5g}%, {b:.5g}%, {a:.5g}%)"
    return fmt.format(r=r, g=g, b=b, a=a)


def rgba_to_hsla(r, g, b, a=None, rgb_scale=RGB_SCALE, hue_scale=HUE_SCALE):
    h, l, s = colorsys.rgb_to_hls(r / rgb_scale, g / rgb_scale, b / rgb_scale)
    return h * hue_scale, s, l, a


def rgba_to_cmyka(r, g, b, a=None, rgb_scale=RGB_SCALE, cmyk_scale=CMYK_SCALE):
    if (r, g, b) == (0, 0, 0):
        # black
        return 0, 0, 0, cmyk_scale

    # rgb [0, rgb_scale] -> cmy [0,1]
    c = 1 - r / rgb_scale
    m = 1 - g / rgb_scale
    y = 1 - b / rgb_scale

    # extract out k [0, 1]
    min_cmy = min(c, m, y)
    c = (c - min_cmy) / (1 - min_cmy)
    m = (m - min_cmy) / (1 - min_cmy)
    y = (y - min_cmy) / (1 - min_cmy)
    k = min_cmy

    # rescale to the range [0, cmyk_scale]
    return c * cmyk_scale, m * cmyk_scale, y * cmyk_scale, k * cmyk_scale
