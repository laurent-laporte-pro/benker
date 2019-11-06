# coding: utf-8
"""
RGB Colors
==========

RGB/RGBA color parser, formatter and converter.
"""

import re

_match_hex8 = re.compile(
    r"^#(?P<r>[0-9a-f]{2})(?P<g>[0-9a-f]{2})(?P<b>[0-9a-f]{2})(?P<a>[0-9a-f]{2})?$", flags=re.I
).match


def parse_hex8(text, rgb_scale=255):
    mo = _match_hex8(text)
    if mo:
        r, g, b, a = mo.group("r", "g", "b", "a")
        k = rgb_scale / 255.0
        r = int(r, 16) * k
        g = int(g, 16) * k
        b = int(b, 16) * k
        if a:
            a = int(a, 16) / 255.0
            return r, g, b, a
        else:
            return r, g, b, None
    else:
        raise ValueError(text)


def format_hex8(r, g, b, a=None, rgb_scale=255):
    k = rgb_scale / 255.0
    r = round(r / k)
    g = round(g / k)
    b = round(b / k)
    if a is None:
        fmt = "#{r:02x}{g:02x}{b:02x}"
    else:
        a = round(a * 255.0)
        fmt = "#{r:02x}{g:02x}{b:02x}{a:02x}"
    return fmt.format(r=r, g=g, b=b, a=a)


def format_hex8_upper(r, g, b, a=None, rgb_scale=255):
    return format_hex8(r, g, b, a=a, rgb_scale=rgb_scale).upper()


def format_hex6(r, g, b, a=None, rgb_scale=255):
    return format_hex8(r, g, b, a=a, rgb_scale=rgb_scale)[:7]


def format_hex6_upper(r, g, b, a=None, rgb_scale=255):
    return format_hex8(r, g, b, a=a, rgb_scale=rgb_scale)[:7].upper()


_match_hex4 = re.compile(r"^#(?P<r>[0-9a-f])(?P<g>[0-9a-f])(?P<b>[0-9a-f])(?P<a>[0-9a-f])?$", flags=re.I).match


def parse_hex4(text, rgb_scale=255):
    mo = _match_hex4(text)
    if mo:
        r, g, b, a = mo.group("r", "g", "b", "a")
        k = rgb_scale / 255.0
        r = int(r * 2, 16) * k
        g = int(g * 2, 16) * k
        b = int(b * 2, 16) * k
        if a:
            a = int(a * 2, 16) / 255.0
            return r, g, b, a
        else:
            return r, g, b, None
    else:
        raise ValueError(text)


def format_hex4(r, g, b, a=None, rgb_scale=255):
    k = rgb_scale / 255.0
    r = round(r / k / 17)
    g = round(g / k / 17)
    b = round(b / k / 17)
    if a is None:
        fmt = "#{r:01x}{g:01x}{b:01x}"
    else:
        a = round(a * 255.0 / 17)
        fmt = "#{r:01x}{g:01x}{b:01x}{a:01x}"
    return fmt.format(r=r, g=g, b=b, a=a)


def format_hex4_upper(r, g, b, a=None, rgb_scale=255):
    return format_hex4(r, g, b, a=a, rgb_scale=rgb_scale).upper()


def format_hex3(r, g, b, a=None, rgb_scale=255):
    return format_hex4(r, g, b, a=a, rgb_scale=rgb_scale)[:4]


def format_hex3_upper(r, g, b, a=None, rgb_scale=255):
    return format_hex4(r, g, b, a=a, rgb_scale=rgb_scale)[:4].upper()


_match_rgba = re.compile(r"^rgba?\(([^)]+)\)$", flags=re.I).match


def _parse_num_value(value, rgb_scale):
    # type: (str, float) -> float
    if value.endswith("%"):
        return float(value[:-1]) * rgb_scale / 100.0
    else:
        return float(value)


def parse_rgba(text, rgb_scale=255):
    mo = _match_rgba(text)
    if mo:
        text = mo.group(1).strip()
        values = re.split(r"\s*,\s*", text)
        if len(values) == 4:
            r, g, b, a = values
        elif len(values) == 3:
            r, g, b = values
            a = None
        else:
            raise ValueError(text)
        try:
            k = rgb_scale / 255.0
            r = _parse_num_value(r, 255) * k
            g = _parse_num_value(g, 255) * k
            b = _parse_num_value(b, 255) * k
            if a:
                a = _parse_num_value(a, 1)
                return r, g, b, a
            else:
                return r, g, b, None
        except ValueError:
            raise ValueError(text)
    else:
        raise ValueError(text)


def format_rgba(r, g, b, a=None, rgb_scale=255):
    k = rgb_scale / 255.0
    r = round(r / k)
    g = round(g / k)
    b = round(b / k)
    if a is None:
        fmt = "rgb({r:g}, {g:g}, {b:g})"
    else:
        fmt = "rgba({r:g}, {g:g}, {b:g}, {a:g})"
    return fmt.format(r=r, g=g, b=b, a=a)


def format_rgba_percent(r, g, b, a=None, rgb_scale=255):
    r = round(r / rgb_scale * 100.0, 2)
    g = round(g / rgb_scale * 100.0, 2)
    b = round(b / rgb_scale * 100.0, 2)
    if a is None:
        fmt = "rgb({r:.5g}%, {g:.5g}%, {b:.5g}%)"
    else:
        a = round(a * 100.0, 2)
        fmt = "rgba({r:.5g}%, {g:.5g}%, {b:.5g}%, {a:.5g}%)"
    return fmt.format(r=r, g=g, b=b, a=a)
