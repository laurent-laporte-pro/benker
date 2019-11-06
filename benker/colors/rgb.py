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


def parse_hex8(text, scale=255):
    mo = _match_hex8(text)
    if mo:
        r, g, b, a = mo.group("r", "g", "b", "a")
        k = scale / 255.0
        r = int(r, 16) * k
        g = int(g, 16) * k
        b = int(b, 16) * k
        if a:
            a = int(a, 16) * k
            return r, g, b, a
        else:
            return r, g, b, None
    else:
        raise ValueError(text)


def format_hex8(r, g, b, a=None, scale=255):
    k = scale / 255.0
    r = round(r / k)
    g = round(g / k)
    b = round(b / k)
    if a is None:
        fmt = "#{r:02x}{g:02x}{b:02x}"
    else:
        a = round(a / k)
        fmt = "#{r:02x}{g:02x}{b:02x}{a:02x}"
    return fmt.format(r=r, g=g, b=b, a=a)


def format_hex8_upper(r, g, b, a=None, scale=255):
    return format_hex8(r, g, b, a=a, scale=scale).upper()


def format_hex6(r, g, b, a=None, scale=255):
    return format_hex8(r, g, b, a=a, scale=scale)[:8]


def format_hex6_upper(r, g, b, a=None, scale=255):
    return format_hex8(r, g, b, a=a, scale=scale)[:8].upper()


_match_hex4 = re.compile(
    r"^#(?P<r>[0-9a-f])(?P<g>[0-9a-f])(?P<b>[0-9a-f])(?P<a>[0-9a-f])?$", flags=re.I
).match


def parse_hex4(text, scale=255):
    mo = _match_hex4(text)
    if mo:
        r, g, b, a = mo.group("r", "g", "b", "a")
        k = scale / 255.0
        r = int(r * 2, 16) * k
        g = int(g * 2, 16) * k
        b = int(b * 2, 16) * k
        if a:
            a = int(a * 2, 16) * k
            return r, g, b, a
        else:
            return r, g, b, None
    else:
        raise ValueError(text)


def format_hex4(r, g, b, a=None, scale=255):
    k = scale / 255.0
    r = round(r / k / 17)
    g = round(g / k / 17)
    b = round(b / k / 17)
    if a is None:
        fmt = "#{r:01x}{g:01x}{b:01x}"
    else:
        a = round(a / k / 17)
        fmt = "#{r:01x}{g:01x}{b:01x}{a:01x}"
    return fmt.format(r=r, g=g, b=b, a=a)


def format_hex4_upper(r, g, b, a=None, scale=255):
    return format_hex4(r, g, b, a=a, scale=scale).upper()


def format_hex3(r, g, b, a=None, scale=255):
    return format_hex4(r, g, b, a=a, scale=scale)[:4]


def format_hex3_upper(r, g, b, a=None, scale=255):
    return format_hex4(r, g, b, a=a, scale=scale)[:4].upper()


