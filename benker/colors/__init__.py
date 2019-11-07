# coding: utf-8
"""
Color spaces conversion
=======================

The :mod:`~benker.colors` module defines various bidirectional conversions
of color values between different color spaces.
"""
from __future__ import division

import colorsys
import re

RGB_SCALE = 255
CMYK_SCALE = 100
HSL_SCALE = 360


def rgb_to_cmyk(r, g, b):
    """
    Convert RGB color to CMYK.

    >>> from benker.colors import rgb_to_cmyk

    >>> rgb_to_cmyk(0, 0, 0)
    (0, 0, 0, 100)
    >>> tuple(map(round, rgb_to_cmyk(9, 83, 224)))
    (96, 63, 0, 12)
    >>> tuple(map(round, rgb_to_cmyk(178, 34, 34)))
    (0, 81, 81, 30)

    :param int or float r: 0 <= red <= 255
    :param int or float g: 0 <= green <= 255
    :param int or float b: 0 <= blue <= 255
    :return: the tuple (c, m, y, k), where 0 <= c, m, y, k <= 100
    """
    if (r, g, b) == (0, 0, 0):
        # black
        return 0, 0, 0, CMYK_SCALE

    # rgb [0,255] -> cmy [0,1]
    c = 1 - r / RGB_SCALE
    m = 1 - g / RGB_SCALE
    y = 1 - b / RGB_SCALE

    # extract out k [0, 1]
    min_cmy = min(c, m, y)
    c = (c - min_cmy) / (1 - min_cmy)
    m = (m - min_cmy) / (1 - min_cmy)
    y = (y - min_cmy) / (1 - min_cmy)
    k = min_cmy

    # rescale to the range [0,CMYK_SCALE]
    return c * CMYK_SCALE, m * CMYK_SCALE, y * CMYK_SCALE, k * CMYK_SCALE


def cmyk_to_rgb(c, m, y, k):
    """
    Convert CMYK color to RGB.

    >>> from benker.colors import cmyk_to_rgb

    >>> cmyk_to_rgb(0, 0, 0, 100)
    (0.0, 0.0, 0.0)
    >>> tuple(map(round, cmyk_to_rgb(96, 63, 0, 12)))
    (9, 83, 224)
    >>> tuple(map(round, cmyk_to_rgb(0, 81, 81, 30)))
    (178, 34, 34)

    :param int or float c: 0 <= cyan <= 100
    :param int or float m: 0 <= magenta <= 100
    :param int or float y: 0 <= yellow <= 100
    :param int or float k: 0 <= black <= 100
    :return: the tuple (r, g, b), where 0 <= r, g, b <= 255
    """
    r = RGB_SCALE * (1.0 - c / CMYK_SCALE) * (1.0 - k / CMYK_SCALE)
    g = RGB_SCALE * (1.0 - m / CMYK_SCALE) * (1.0 - k / CMYK_SCALE)
    b = RGB_SCALE * (1.0 - y / CMYK_SCALE) * (1.0 - k / CMYK_SCALE)
    return r, g, b


def _parse_value(value, scale):
    mo = re.match(r"^(\d+(?:.\d+)?)(%)?$", value)
    if mo:
        if mo.group(2):
            return float(mo.group(1)) * scale / 100
        else:
            return float(mo.group(1))
    else:
        raise ValueError(value)


#: CSS color names, see: `<https://www.w3.org/TR/css-color-3/#svg-color>`_
# Color name: rgb
CSS_COLOR_NAMES = {
    "aliceblue": (240, 248, 255),
    "antiquewhite": (250, 235, 215),
    "aqua": (0, 255, 255),
    "aquamarine": (127, 255, 212),
    "azure": (240, 255, 255),
    "beige": (245, 245, 220),
    "bisque": (255, 228, 196),
    "black": (0, 0, 0),
    "blanchedalmond": (255, 235, 205),
    "blue": (0, 0, 255),
    "blueviolet": (138, 43, 226),
    "brown": (165, 42, 42),
    "burlywood": (222, 184, 135),
    "cadetblue": (95, 158, 160),
    "chartreuse": (127, 255, 0),
    "chocolate": (210, 105, 30),
    "coral": (255, 127, 80),
    "cornflowerblue": (100, 149, 237),
    "cornsilk": (255, 248, 220),
    "crimson": (220, 20, 60),
    "cyan": (0, 255, 255),
    "darkblue": (0, 0, 139),
    "darkcyan": (0, 139, 139),
    "darkgoldenrod": (184, 134, 11),
    "darkgray": (169, 169, 169),
    "darkgreen": (0, 100, 0),
    "darkgrey": (169, 169, 169),
    "darkkhaki": (189, 183, 107),
    "darkmagenta": (139, 0, 139),
    "darkolivegreen": (85, 107, 47),
    "darkorange": (255, 140, 0),
    "darkorchid": (153, 50, 204),
    "darkred": (139, 0, 0),
    "darksalmon": (233, 150, 122),
    "darkseagreen": (143, 188, 143),
    "darkslateblue": (72, 61, 139),
    "darkslategray": (47, 79, 79),
    "darkslategrey": (47, 79, 79),
    "darkturquoise": (0, 206, 209),
    "darkviolet": (148, 0, 211),
    "deeppink": (255, 20, 147),
    "deepskyblue": (0, 191, 255),
    "dimgray": (105, 105, 105),
    "dimgrey": (105, 105, 105),
    "dodgerblue": (30, 144, 255),
    "firebrick": (178, 34, 34),
    "floralwhite": (255, 250, 240),
    "forestgreen": (34, 139, 34),
    "fuchsia": (255, 0, 255),
    "gainsboro": (220, 220, 220),
    "ghostwhite": (248, 248, 255),
    "gold": (255, 215, 0),
    "goldenrod": (218, 165, 32),
    "gray": (128, 128, 128),
    "green": (0, 128, 0),
    "greenyellow": (173, 255, 47),
    "grey": (128, 128, 128),
    "honeydew": (240, 255, 240),
    "hotpink": (255, 105, 180),
    "indianred": (205, 92, 92),
    "indigo": (75, 0, 130),
    "ivory": (255, 255, 240),
    "khaki": (240, 230, 140),
    "lavender": (230, 230, 250),
    "lavenderblush": (255, 240, 245),
    "lawngreen": (124, 252, 0),
    "lemonchiffon": (255, 250, 205),
    "lightblue": (173, 216, 230),
    "lightcoral": (240, 128, 128),
    "lightcyan": (224, 255, 255),
    "lightgoldenrodyellow": (250, 250, 210),
    "lightgray": (211, 211, 211),
    "lightgreen": (144, 238, 144),
    "lightgrey": (211, 211, 211),
    "lightpink": (255, 182, 193),
    "lightsalmon": (255, 160, 122),
    "lightseagreen": (32, 178, 170),
    "lightskyblue": (135, 206, 250),
    "lightslategray": (119, 136, 153),
    "lightslategrey": (119, 136, 153),
    "lightsteelblue": (176, 196, 222),
    "lightyellow": (255, 255, 224),
    "lime": (0, 255, 0),
    "limegreen": (50, 205, 50),
    "linen": (250, 240, 230),
    "magenta": (255, 0, 255),
    "maroon": (128, 0, 0),
    "mediumaquamarine": (102, 205, 170),
    "mediumblue": (0, 0, 205),
    "mediumorchid": (186, 85, 211),
    "mediumpurple": (147, 112, 219),
    "mediumseagreen": (60, 179, 113),
    "mediumslateblue": (123, 104, 238),
    "mediumspringgreen": (0, 250, 154),
    "mediumturquoise": (72, 209, 204),
    "mediumvioletred": (199, 21, 133),
    "midnightblue": (25, 25, 112),
    "mintcream": (245, 255, 250),
    "mistyrose": (255, 228, 225),
    "moccasin": (255, 228, 181),
    "navajowhite": (255, 222, 173),
    "navy": (0, 0, 128),
    "oldlace": (253, 245, 230),
    "olive": (128, 128, 0),
    "olivedrab": (107, 142, 35),
    "orange": (255, 165, 0),
    "orangered": (255, 69, 0),
    "orchid": (218, 112, 214),
    "palegoldenrod": (238, 232, 170),
    "palegreen": (152, 251, 152),
    "paleturquoise": (175, 238, 238),
    "palevioletred": (219, 112, 147),
    "papayawhip": (255, 239, 213),
    "peachpuff": (255, 218, 185),
    "peru": (205, 133, 63),
    "pink": (255, 192, 203),
    "plum": (221, 160, 221),
    "powderblue": (176, 224, 230),
    "purple": (128, 0, 128),
    "red": (255, 0, 0),
    "rosybrown": (188, 143, 143),
    "royalblue": (65, 105, 225),
    "saddlebrown": (139, 69, 19),
    "salmon": (250, 128, 114),
    "sandybrown": (244, 164, 96),
    "seagreen": (46, 139, 87),
    "seashell": (255, 245, 238),
    "sienna": (160, 82, 45),
    "silver": (192, 192, 192),
    "skyblue": (135, 206, 235),
    "slateblue": (106, 90, 205),
    "slategray": (112, 128, 144),
    "slategrey": (112, 128, 144),
    "snow": (255, 250, 250),
    "springgreen": (0, 255, 127),
    "steelblue": (70, 130, 180),
    "tan": (210, 180, 140),
    "teal": (0, 128, 128),
    "thistle": (216, 191, 216),
    "tomato": (255, 99, 71),
    "turquoise": (64, 224, 208),
    "violet": (238, 130, 238),
    "wheat": (245, 222, 179),
    "white": (255, 255, 255),
    "whitesmoke": (245, 245, 245),
    "yellow": (255, 255, 0),
    "yellowgreen": (154, 205, 50),
}

_COLOR_NAME_REGEX = "|".join(sorted(CSS_COLOR_NAMES, key=lambda n: -len(n)))

_match_hex8 = re.compile(r"^#((?:[\da-f]{2}))((?:[\da-f]{2}))((?:[\da-f]{2}))((?:[\da-f]{2}))?$", flags=re.I).match
_match_hex4 = re.compile(r"^#((?:[\da-f]))((?:[\da-f]))((?:[\da-f]))((?:[\da-f]))?$", flags=re.I).match
_match_rgba = re.compile(r"^rgba?\(([^)]+)\)$").match
_match_hsla = re.compile(r"^hsla?\(([^)]+)\)$").match
_match_cmyk = re.compile(r"^cmyk?\(([^)]+)\)$").match
_match_name = re.compile(r"^{}$".format(_COLOR_NAME_REGEX), flags=re.I).match

# 3B2 color space
_match_cmyk_ext = re.compile(r"^{\(([^)]+)}$").match
_match_percent_name = re.compile(r"^(\d+(?:\.\d+)?%)({})$".format(_COLOR_NAME_REGEX), flags=re.I).match
_match_other_name = re.compile(r"^(\w+)$").match


class RGBColor(object):
    """
    RGB color

    Usage:

    >>> from benker.colors import RGBColor

    >>> RGBColor.from_string("#00FF00")
    RGBColor(0, 255, 0)
    >>> RGBColor.from_string("#00FF0080")
    RGBColor(0, 255, 0, 128)

    >>> RGBColor.from_string(" rgb(64, 128, 192)")
    RGBColor(64.0, 128.0, 192.0)
    >>> RGBColor.from_string(" rgba(64, 128, 192, .75)")
    RGBColor(64.0, 128.0, 192.0, 1.0)
    >>> RGBColor.from_string(" rgba(64, 128, 192, 100%)")
    RGBColor(64.0, 128.0, 192.0, 1.0)

    >>> RGBColor.from_string("#AABBCC")
    RGBColor(170, 187, 204)
    >>> RGBColor.from_string("#abc")
    RGBColor(170, 187, 204)
    >>> RGBColor.from_string("#abc7")
    RGBColor(170, 187, 204, 119)

    >>> RGBColor.from_string("LightYellow")
    RGBColor(255, 255, 224)
    """

    __slots__ = ("r", "g", "b", "a", "name")

    def __init__(self, r, g, b, a=None, name=None):
        """
        Construct a RGB color

        :param r: 0 <= r <= 255
        :param g: 0 <= g <= 255
        :param b: 0 <= b <= 255
        :param a: 0 <= a <= 1 or ``None``
        :param name: name of a CSS or PANTONE color, eg.: "Pantone_Reflex_Blue_CVC".
        """
        self.r = r  # 0 <= r <= RGB_SCALE
        self.g = g  # 0 <= g <= RGB_SCALE
        self.b = b  # 0 <= b <= RGB_SCALE
        self.a = a  # 0 <= a <= 1 or None
        self.name = name

    def to_rgba(self, ndigits=2):
        r, g, b, a, name = self.r, self.g, self.b, self.a, self.name
        if name:
            return name
        elif a is not None:
            fmt = "rgba({{r:.{0}f}}, {{g:.{0}f}}, {{b:.{0}f}}, {{a:.2f}})".format(ndigits)
            return fmt.format(r=r, g=g, b=b, a=a)
        else:
            fmt = "rgb({{r:.{0}f}}, {{g:.{0}f}}, {{b:.{0}f}})".format(ndigits)
            return fmt.format(r=r, g=g, b=b, a=a)

    def to_hsla(self, ndigits=2):
        # fixme
        h, l, s = colorsys.rgb_to_hls(self.r, self.g, self.b)
        a, name = self.a, self.name
        if name:
            return name
        elif a is not None:
            fmt = "hsla({{h:.{0}f}}, {{l:.{0}f}}, {{b:.{0}f}}, {{a:.2f}})".format(ndigits)
            return fmt.format(r=r, g=g, b=b, a=a)
        else:
            fmt = "hsl({{h:.{0}f}}, {{l:.{0}f}}, {{b:.{0}f}})".format(ndigits)
            return fmt.format(r=r, g=g, b=b, a=a)

    def __str__(self):
        return self.to_rgba(ndigits=0)

    def __repr__(self):
        cls = self.__class__.__name__
        r, g, b, a, name = self.r, self.g, self.b, self.a, self.name
        if a is None:
            if name is None:
                fmt = "{cls}({r!r}, {g!r}, {b!r})"
            else:
                fmt = "{cls}({r!r}, {g!r}, {b!r}, name={name!r})"
        else:
            if name is None:
                fmt = "{cls}({r!r}, {g!r}, {b!r}, {a!r})"
            else:
                fmt = "{cls}({r!r}, {g!r}, {b!r}, {a!r}, name={name!r})"
        return fmt.format(cls=cls, r=r, g=g, b=b, a=a, name=name)

    @classmethod
    def from_string(cls, text):
        text = text.strip()
        rules = [
            (_match_hex8, cls._parse_hex8),
            (_match_hex4, cls._parse_hex4),
            (_match_rgba, cls._parse_rgba),
            (_match_hsla, cls._parse_hsla),
            (_match_cmyk, cls._parse_cmyk),
            (_match_cmyk_ext, cls._parse_cmyk),
            (_match_name, cls._parse_name),
            (_match_percent_name, cls._parse_percent_name),
            (_match_other_name, cls._parse_other_name),
        ]
        for matcher, parser in rules:
            mo = matcher(text)
            if mo:
                try:
                    return parser(mo)
                except ValueError:
                    raise ValueError(text)
        else:
            raise ValueError(text)

    @classmethod
    def _parse_rgba(cls, mo):
        text = mo.group(1)
        values = re.split(r",\s*", text)
        if len(values) == 4:
            r, g, b, a = values
        elif len(values) == 3:
            r, g, b = values
            a = None
        else:
            raise ValueError(text)
        r = _parse_value(r, RGB_SCALE)
        g = _parse_value(g, RGB_SCALE)
        b = _parse_value(b, RGB_SCALE)
        a = _parse_value(a, 1) if a else None
        return cls(r, g, b, a)

    @classmethod
    def _parse_hsla(cls, mo):
        text = mo.group(1)
        values = re.split(r",\s*", text)
        if len(values) == 4:
            h, s, l, a = values
        elif len(values) == 3:
            h, s, l = values
            a = None
        else:
            raise ValueError(text)
        h = _parse_value(h, HSL_SCALE)
        s = _parse_value(s, 1)
        l = _parse_value(l, 1)
        a = _parse_value(a, 1) if a else None
        r, g, b = colorsys.hls_to_rgb(h, l, s)
        return cls(r, g, b, a)

    @classmethod
    def _parse_cmyk(cls, mo):
        text = mo.group(1)
        values = re.split(r",\s*", text)
        if len(values) == 4:
            c, m, y, k = values
        else:
            raise ValueError(text)
        c = _parse_value(c, CMYK_SCALE)
        m = _parse_value(m, CMYK_SCALE)
        y = _parse_value(y, CMYK_SCALE)
        k = _parse_value(k, CMYK_SCALE)
        r, g, b = cmyk_to_rgb(c, m, y, k)
        return cls(r, g, b)

    @classmethod
    def _parse_hex8(cls, mo):
        r, g, b, a = mo.group(1, 2, 3, 4)
        r = int(r, 16)
        g = int(g, 16)
        b = int(b, 16)
        a = int(a, 16) if a else None
        return cls(r, g, b, a)

    @classmethod
    def _parse_hex4(cls, mo):
        r, g, b, a = mo.group(1, 2, 3, 4)
        r = int(r * 2, 16)
        g = int(g * 2, 16)
        b = int(b * 2, 16)
        a = int(a * 2, 16) if a else None
        return cls(r, g, b, a)

    @classmethod
    def _parse_name(cls, mo):
        color_name = mo.group()
        r, g, b = CSS_COLOR_NAMES[color_name.lower()]
        return cls(r, g, b)

    @classmethod
    def _parse_percent_name(cls, mo):
        p, color_name = mo.group(1, 2)
        p = _parse_value(p, 1)
        r, g, b = CSS_COLOR_NAMES[color_name.lower()]
        return cls(r * p, g * p, b * p, name=mo.group())

    @classmethod
    def _parse_other_name(cls, mo):
        return cls(None, None, None, name=mo.group(1))
