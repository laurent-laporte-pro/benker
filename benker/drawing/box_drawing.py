# coding: utf-8
import collections
import enum

from benker.units import convert_value


class Style(enum.Enum):
    NONE = ""
    LIGHT = "Light"
    HEAVY = "Heavy"
    DOUBLE = "Double"
    ARC = "Arc"
    LIGHT_DOUBLE_DASH = "Light Double Dash"
    HEAVY_DOUBLE_DASH = "Heavy Double Dash"
    LIGHT_TRIPLE_DASH = "Light Triple Dash"
    HEAVY_TRIPLE_DASH = "Heavy Triple Dash"
    LIGHT_QUADRUPLE_DASH = "Light Quadruple Dash"
    HEAVY_QUADRUPLE_DASH = "Heavy Quadruple Dash"

    def __add__(self, other):
        if other is Style.NONE:
            return self
        return other

    def __sub__(self, other):
        if other is Style.NONE:
            return self
        return Style.NONE

    @classmethod
    def from_css(cls, style, width):
        width_pt = convert_value(width)
        if width_pt == 0.0:
            return Style.NONE
        elif width_pt <= 1:
            default_style = Style.LIGHT
            mapping = {
                'dotted': Style.LIGHT_QUADRUPLE_DASH,
                'dashed': Style.LIGHT_DOUBLE_DASH,
                'solid': Style.LIGHT,
                'double': Style.DOUBLE,
                'none': Style.NONE,
                'hidden': Style.NONE,
            }
        else:
            default_style = Style.HEAVY
            mapping = {
                'dotted': Style.HEAVY_QUADRUPLE_DASH,
                'dashed': Style.HEAVY_DOUBLE_DASH,
                'solid': Style.HEAVY,
                'double': Style.DOUBLE,
                'none': Style.NONE,
                'hidden': Style.NONE,
            }
        return mapping.get(style, default_style)


Symbol = collections.namedtuple('Symbol', ['char', 'left', 'right', 'up', 'down'])

SYMBOL_TABLE = [
    # white space
    Symbol(u' ', Style.NONE, Style.NONE, Style.NONE, Style.NONE),

    # box drawing symbols
    Symbol(u'─', Style.LIGHT, Style.LIGHT, Style.NONE, Style.NONE),
    Symbol(u'━', Style.HEAVY, Style.HEAVY, Style.NONE, Style.NONE),
    Symbol(u'│', Style.NONE, Style.NONE, Style.LIGHT, Style.LIGHT),
    Symbol(u'┃', Style.NONE, Style.NONE, Style.HEAVY, Style.HEAVY),
    Symbol(u'┄', Style.LIGHT_TRIPLE_DASH, Style.LIGHT_TRIPLE_DASH, Style.NONE, Style.NONE),
    Symbol(u'┅', Style.HEAVY_TRIPLE_DASH, Style.HEAVY_TRIPLE_DASH, Style.NONE, Style.NONE),
    Symbol(u'┆', Style.NONE, Style.NONE, Style.LIGHT_TRIPLE_DASH, Style.LIGHT_TRIPLE_DASH),
    Symbol(u'┇', Style.NONE, Style.NONE, Style.HEAVY_TRIPLE_DASH, Style.HEAVY_TRIPLE_DASH),
    Symbol(u'┈', Style.LIGHT_QUADRUPLE_DASH, Style.LIGHT_QUADRUPLE_DASH, Style.NONE, Style.NONE),
    Symbol(u'┉', Style.HEAVY_QUADRUPLE_DASH, Style.HEAVY_QUADRUPLE_DASH, Style.NONE, Style.NONE),
    Symbol(u'┊', Style.NONE, Style.NONE, Style.LIGHT_QUADRUPLE_DASH, Style.LIGHT_QUADRUPLE_DASH),
    Symbol(u'┋', Style.NONE, Style.NONE, Style.HEAVY_QUADRUPLE_DASH, Style.HEAVY_QUADRUPLE_DASH),
    Symbol(u'┌', Style.NONE, Style.LIGHT, Style.NONE, Style.LIGHT),
    Symbol(u'┍', Style.NONE, Style.HEAVY, Style.NONE, Style.LIGHT),
    Symbol(u'┎', Style.NONE, Style.LIGHT, Style.NONE, Style.HEAVY),
    Symbol(u'┏', Style.NONE, Style.HEAVY, Style.NONE, Style.HEAVY),
    Symbol(u'┐', Style.LIGHT, Style.NONE, Style.NONE, Style.LIGHT),
    Symbol(u'┑', Style.HEAVY, Style.NONE, Style.NONE, Style.LIGHT),
    Symbol(u'┒', Style.LIGHT, Style.NONE, Style.NONE, Style.HEAVY),
    Symbol(u'┓', Style.HEAVY, Style.NONE, Style.NONE, Style.HEAVY),
    Symbol(u'└', Style.NONE, Style.LIGHT, Style.LIGHT, Style.NONE),
    Symbol(u'┕', Style.NONE, Style.HEAVY, Style.LIGHT, Style.NONE),
    Symbol(u'┖', Style.NONE, Style.LIGHT, Style.HEAVY, Style.NONE),
    Symbol(u'┗', Style.NONE, Style.HEAVY, Style.HEAVY, Style.NONE),
    Symbol(u'┘', Style.LIGHT, Style.NONE, Style.LIGHT, Style.NONE),
    Symbol(u'┙', Style.HEAVY, Style.NONE, Style.LIGHT, Style.NONE),
    Symbol(u'┚', Style.LIGHT, Style.NONE, Style.HEAVY, Style.NONE),
    Symbol(u'┛', Style.HEAVY, Style.NONE, Style.HEAVY, Style.NONE),
    Symbol(u'├', Style.NONE, Style.LIGHT, Style.LIGHT, Style.LIGHT),
    Symbol(u'┝', Style.NONE, Style.HEAVY, Style.LIGHT, Style.LIGHT),
    Symbol(u'┞', Style.NONE, Style.LIGHT, Style.HEAVY, Style.LIGHT),
    Symbol(u'┟', Style.NONE, Style.LIGHT, Style.LIGHT, Style.HEAVY),
    Symbol(u'┠', Style.NONE, Style.LIGHT, Style.HEAVY, Style.HEAVY),
    Symbol(u'┡', Style.NONE, Style.HEAVY, Style.HEAVY, Style.LIGHT),
    Symbol(u'┢', Style.NONE, Style.HEAVY, Style.LIGHT, Style.HEAVY),
    Symbol(u'┣', Style.NONE, Style.HEAVY, Style.HEAVY, Style.HEAVY),
    Symbol(u'┤', Style.LIGHT, Style.NONE, Style.LIGHT, Style.LIGHT),
    Symbol(u'┥', Style.HEAVY, Style.NONE, Style.LIGHT, Style.LIGHT),
    Symbol(u'┦', Style.LIGHT, Style.NONE, Style.HEAVY, Style.LIGHT),
    Symbol(u'┧', Style.LIGHT, Style.NONE, Style.LIGHT, Style.HEAVY),
    Symbol(u'┨', Style.LIGHT, Style.NONE, Style.HEAVY, Style.HEAVY),
    Symbol(u'┩', Style.HEAVY, Style.NONE, Style.HEAVY, Style.LIGHT),
    Symbol(u'┪', Style.HEAVY, Style.NONE, Style.LIGHT, Style.HEAVY),
    Symbol(u'┫', Style.HEAVY, Style.NONE, Style.HEAVY, Style.HEAVY),
    Symbol(u'┬', Style.LIGHT, Style.LIGHT, Style.NONE, Style.LIGHT),
    Symbol(u'┭', Style.HEAVY, Style.LIGHT, Style.NONE, Style.LIGHT),
    Symbol(u'┮', Style.LIGHT, Style.HEAVY, Style.NONE, Style.LIGHT),
    Symbol(u'┯', Style.HEAVY, Style.HEAVY, Style.NONE, Style.LIGHT),
    Symbol(u'┰', Style.LIGHT, Style.LIGHT, Style.NONE, Style.HEAVY),
    Symbol(u'┱', Style.HEAVY, Style.LIGHT, Style.NONE, Style.HEAVY),
    Symbol(u'┲', Style.LIGHT, Style.HEAVY, Style.NONE, Style.HEAVY),
    Symbol(u'┳', Style.HEAVY, Style.HEAVY, Style.NONE, Style.HEAVY),
    Symbol(u'┴', Style.LIGHT, Style.LIGHT, Style.LIGHT, Style.NONE),
    Symbol(u'┵', Style.HEAVY, Style.LIGHT, Style.LIGHT, Style.NONE),
    Symbol(u'┶', Style.LIGHT, Style.HEAVY, Style.LIGHT, Style.NONE),
    Symbol(u'┷', Style.HEAVY, Style.HEAVY, Style.LIGHT, Style.NONE),
    Symbol(u'┸', Style.LIGHT, Style.LIGHT, Style.HEAVY, Style.NONE),
    Symbol(u'┹', Style.HEAVY, Style.LIGHT, Style.HEAVY, Style.NONE),
    Symbol(u'┺', Style.LIGHT, Style.HEAVY, Style.HEAVY, Style.NONE),
    Symbol(u'┻', Style.HEAVY, Style.HEAVY, Style.HEAVY, Style.NONE),
    Symbol(u'┼', Style.LIGHT, Style.LIGHT, Style.LIGHT, Style.LIGHT),
    Symbol(u'┽', Style.HEAVY, Style.LIGHT, Style.LIGHT, Style.LIGHT),
    Symbol(u'┾', Style.LIGHT, Style.HEAVY, Style.LIGHT, Style.LIGHT),
    Symbol(u'┿', Style.HEAVY, Style.HEAVY, Style.LIGHT, Style.LIGHT),
    Symbol(u'╀', Style.LIGHT, Style.LIGHT, Style.HEAVY, Style.LIGHT),
    Symbol(u'╁', Style.LIGHT, Style.LIGHT, Style.LIGHT, Style.HEAVY),
    Symbol(u'╂', Style.LIGHT, Style.LIGHT, Style.HEAVY, Style.HEAVY),
    Symbol(u'╃', Style.HEAVY, Style.LIGHT, Style.HEAVY, Style.LIGHT),
    Symbol(u'╄', Style.LIGHT, Style.HEAVY, Style.HEAVY, Style.LIGHT),
    Symbol(u'╅', Style.HEAVY, Style.LIGHT, Style.LIGHT, Style.HEAVY),
    Symbol(u'╆', Style.LIGHT, Style.HEAVY, Style.LIGHT, Style.HEAVY),
    Symbol(u'╇', Style.HEAVY, Style.HEAVY, Style.HEAVY, Style.LIGHT),
    Symbol(u'╈', Style.HEAVY, Style.HEAVY, Style.LIGHT, Style.HEAVY),
    Symbol(u'╉', Style.HEAVY, Style.LIGHT, Style.HEAVY, Style.HEAVY),
    Symbol(u'╊', Style.LIGHT, Style.HEAVY, Style.HEAVY, Style.HEAVY),
    Symbol(u'╋', Style.HEAVY, Style.HEAVY, Style.HEAVY, Style.HEAVY),
    Symbol(u'╌', Style.LIGHT_DOUBLE_DASH, Style.LIGHT_DOUBLE_DASH, Style.NONE, Style.NONE),
    Symbol(u'╍', Style.HEAVY_DOUBLE_DASH, Style.HEAVY_DOUBLE_DASH, Style.NONE, Style.NONE),
    Symbol(u'╎', Style.NONE, Style.NONE, Style.LIGHT_DOUBLE_DASH, Style.LIGHT_DOUBLE_DASH),
    Symbol(u'╏', Style.NONE, Style.NONE, Style.HEAVY_DOUBLE_DASH, Style.HEAVY_DOUBLE_DASH),
    Symbol(u'═', Style.DOUBLE, Style.DOUBLE, Style.NONE, Style.NONE),
    Symbol(u'║', Style.NONE, Style.NONE, Style.DOUBLE, Style.DOUBLE),
    Symbol(u'╒', Style.NONE, Style.DOUBLE, Style.NONE, Style.LIGHT),
    Symbol(u'╓', Style.NONE, Style.LIGHT, Style.NONE, Style.DOUBLE),
    Symbol(u'╔', Style.NONE, Style.DOUBLE, Style.NONE, Style.DOUBLE),
    Symbol(u'╕', Style.DOUBLE, Style.NONE, Style.NONE, Style.LIGHT),
    Symbol(u'╖', Style.LIGHT, Style.NONE, Style.NONE, Style.DOUBLE),
    Symbol(u'╗', Style.DOUBLE, Style.NONE, Style.NONE, Style.DOUBLE),
    Symbol(u'╘', Style.NONE, Style.DOUBLE, Style.LIGHT, Style.NONE),
    Symbol(u'╙', Style.NONE, Style.LIGHT, Style.DOUBLE, Style.NONE),
    Symbol(u'╚', Style.NONE, Style.DOUBLE, Style.DOUBLE, Style.NONE),
    Symbol(u'╛', Style.DOUBLE, Style.NONE, Style.LIGHT, Style.NONE),
    Symbol(u'╜', Style.LIGHT, Style.NONE, Style.DOUBLE, Style.NONE),
    Symbol(u'╝', Style.DOUBLE, Style.NONE, Style.DOUBLE, Style.NONE),
    Symbol(u'╞', Style.NONE, Style.DOUBLE, Style.LIGHT, Style.LIGHT),
    Symbol(u'╟', Style.NONE, Style.LIGHT, Style.DOUBLE, Style.DOUBLE),
    Symbol(u'╠', Style.NONE, Style.DOUBLE, Style.DOUBLE, Style.DOUBLE),
    Symbol(u'╡', Style.DOUBLE, Style.NONE, Style.LIGHT, Style.LIGHT),
    Symbol(u'╢', Style.LIGHT, Style.NONE, Style.DOUBLE, Style.DOUBLE),
    Symbol(u'╣', Style.DOUBLE, Style.NONE, Style.DOUBLE, Style.DOUBLE),
    Symbol(u'╤', Style.DOUBLE, Style.DOUBLE, Style.NONE, Style.LIGHT),
    Symbol(u'╥', Style.LIGHT, Style.LIGHT, Style.NONE, Style.DOUBLE),
    Symbol(u'╦', Style.DOUBLE, Style.DOUBLE, Style.NONE, Style.DOUBLE),
    Symbol(u'╧', Style.DOUBLE, Style.DOUBLE, Style.LIGHT, Style.NONE),
    Symbol(u'╨', Style.LIGHT, Style.LIGHT, Style.DOUBLE, Style.NONE),
    Symbol(u'╩', Style.DOUBLE, Style.DOUBLE, Style.DOUBLE, Style.NONE),
    Symbol(u'╪', Style.DOUBLE, Style.DOUBLE, Style.LIGHT, Style.LIGHT),
    Symbol(u'╫', Style.LIGHT, Style.LIGHT, Style.DOUBLE, Style.DOUBLE),
    Symbol(u'╬', Style.DOUBLE, Style.DOUBLE, Style.DOUBLE, Style.DOUBLE),
    Symbol(u'╭', Style.NONE, Style.ARC, Style.NONE, Style.ARC),
    Symbol(u'╮', Style.ARC, Style.NONE, Style.NONE, Style.ARC),
    Symbol(u'╯', Style.ARC, Style.NONE, Style.ARC, Style.NONE),
    Symbol(u'╰', Style.NONE, Style.ARC, Style.ARC, Style.NONE),
    # Symbol(u'╱', Style.NONE, Style.NONE, Style.NONE, Style.NONE),
    # Symbol(u'╲', Style.NONE, Style.NONE, Style.NONE, Style.NONE),
    # Symbol(u'╳', Style.NONE, Style.NONE, Style.NONE, Style.NONE),
    Symbol(u'╴', Style.LIGHT, Style.NONE, Style.NONE, Style.NONE),
    Symbol(u'╵', Style.NONE, Style.NONE, Style.LIGHT, Style.NONE),
    Symbol(u'╶', Style.NONE, Style.LIGHT, Style.NONE, Style.NONE),
    Symbol(u'╷', Style.NONE, Style.NONE, Style.NONE, Style.LIGHT),
    Symbol(u'╸', Style.HEAVY, Style.NONE, Style.NONE, Style.NONE),
    Symbol(u'╹', Style.NONE, Style.NONE, Style.HEAVY, Style.NONE),
    Symbol(u'╺', Style.NONE, Style.HEAVY, Style.NONE, Style.NONE),
    Symbol(u'╻', Style.NONE, Style.NONE, Style.NONE, Style.HEAVY),
    Symbol(u'╼', Style.LIGHT, Style.HEAVY, Style.NONE, Style.NONE),
    Symbol(u'╽', Style.NONE, Style.NONE, Style.LIGHT, Style.HEAVY),
    Symbol(u'╾', Style.HEAVY, Style.LIGHT, Style.NONE, Style.NONE),
    Symbol(u'╿', Style.NONE, Style.NONE, Style.HEAVY, Style.LIGHT)]

CHAR_TO_STYLES_MAP = {s.char: s[1:] for s in SYMBOL_TABLE}
STYLES_TO_CHAR_MAP = {s: c for c, s in CHAR_TO_STYLES_MAP.items()}


def get_char_from_styles(styles):
    for attempt in Style:
        attempt = None if attempt is Style.NONE else attempt
        if attempt in styles:
            styles = tuple(Style.LIGHT if style is attempt else style for style in styles)
        try:
            return STYLES_TO_CHAR_MAP[styles]
        except KeyError:
            pass
    raise KeyError(styles)


def mask_add(c1, c2):
    styles1 = CHAR_TO_STYLES_MAP[c1]
    styles2 = CHAR_TO_STYLES_MAP[c2]
    styles = tuple(style1 + style2 for style1, style2 in zip(styles1, styles2))
    try:
        return get_char_from_styles(styles)
    except KeyError:
        raise KeyError((c1, c2))


def horizontal(length, style=Style.LIGHT):
    first_styles = (Style.NONE, style, Style.NONE, Style.NONE)
    middle_styles = (style, style, Style.NONE, Style.NONE)
    last_styles = (style, Style.NONE, Style.NONE, Style.NONE)
    first_char = get_char_from_styles(first_styles)
    middle_char = get_char_from_styles(middle_styles)
    last_char = get_char_from_styles(last_styles)
    if length == 0:
        return ""
    elif length == 1:
        return middle_char
    else:
        return first_char + middle_char * (length - 2) + last_char


def vertical(length, style=Style.LIGHT):
    first_styles = (Style.NONE, Style.NONE, Style.NONE, style)
    middle_styles = (Style.NONE, Style.NONE, style, style)
    last_styles = (Style.NONE, Style.NONE, style, Style.NONE)
    first_char = get_char_from_styles(first_styles)
    middle_char = get_char_from_styles(middle_styles)
    last_char = get_char_from_styles(last_styles)
    if length == 0:
        return ""
    elif length == 1:
        return middle_char
    else:
        return first_char + middle_char * (length - 2) + last_char
