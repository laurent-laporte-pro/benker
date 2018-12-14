# coding: utf-8
"""
Canvas use for drawing
"""

from benker.drawing.box_drawing import mask_add, horizontal, vertical, Style

WHITE = u" "

RIGHT = u"\u257a"
RIGHT_LEFT = u"\u2501"
LEFT = u"\u2578"

BOTTOM = u"\u257b"
TOP_BOTTOM = u"\u2503"
TOP = u"\u2579"

LIGHT_HORIZONTAL = RIGHT + RIGHT_LEFT + LEFT
LIGHT_VERTICAL = BOTTOM + TOP_BOTTOM + TOP


class Canvas(object):
    """
    Canvas use for drawing
    """

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self._lines = [WHITE * width for _ in range(height)]

    def __str__(self):
        return "\n".join(self._lines)

    def __getitem__(self, coord):
        x, y = coord
        try:
            return self._lines[y][x]
        except IndexError:
            raise IndexError(coord)

    def __setitem__(self, coord, char):
        assert len(char) == 1
        x, y = coord
        line = self._lines[y]
        line = line[:x] + char + line[x + 1:]
        self._lines[y] = line

    def __delitem__(self, coord):
        self[coord] = WHITE

    def line(self, x0, y0, x1, y1, style=Style.LIGHT):
        if x1 >= x0:
            length_x = 1 + x1 - x0
            sx = 1
        else:
            length_x = 1 + x0 - x1
            sx = -1
        if y1 >= y0:
            length_y = 1 + y1 - y0
            sy = 1
        else:
            length_y = 1 + y0 - y1
            sy = -1
        if length_x >= length_y:
            length = length_x
            s = sx
            symbols = horizontal(length, style)
        else:
            length = length_y
            s = sy
            symbols = vertical(length, style)
        if length == 1:
            return
        symbols = symbols[::s]
        for pos in range(length):
            x = x0 + int(sx * length_x * pos / length)
            y = y0 + int(sy * length_y * pos / length)
            c1 = self[(x, y)]
            self[(x, y)] = mask_add(c1, symbols[pos])

    def box(self, x0, y0, x1, y1, styles=None, widths=None, radius=None):
        styles = [] if styles is None else [styles] * 4 if isinstance(styles, str) else styles
        styles = styles + ['solid'] * (4 - len(styles))
        widths = [] if widths is None else [widths] * 4 if isinstance(widths, str) else widths
        widths = widths + ['1pt'] * (4 - len(widths))
        radius = [] if radius is None else [radius] * 4 if isinstance(radius, str) else radius
        radius = radius + ['0pt'] * (4 - len(radius))
        self.line(x0, y0, x1, y0, style=Style.from_css(styles[0], widths[0]))
        self.line(x1, y0, x1, y1, style=Style.from_css(styles[1], widths[1]))
        self.line(x1, y1, x0, y1, style=Style.from_css(styles[2], widths[2]))
        self.line(x0, y1, x0, y0, style=Style.from_css(styles[3], widths[3]))

    def text(self, x0, y0, texts):
        for y, text in enumerate(texts, y0):
            line = self._lines[y]
            line = line[:x0] + text + line[x0 + len(text):]
            self._lines[y] = line


c = Canvas(20, 10)
c.box(0, 0, 19, 9, styles=['solid', 'double', 'dotted', 'dashed'], widths='2')
c.box(9, 4, 10, 6)
c.box(4, 2, 7, 4)
c.box(12, 2, 15, 4)
c.line(6, 6, 7, 7)
c.box(7, 7, 12, 8)
c.line(12, 7, 13, 6)
print(c)
