# coding: utf-8
"""
Grid Cell
=========

A :class:`~benker.cell.Cell` object stores the *content* of a :class:`~benker.grid.Grid` cell.

A cell can have *styles*, a dictionary of key-value properties attached to the cell.

The cell *type* is "body" by default, but can also be "header", "footer" or whatever…

The cell *width* and *height* is (1, 1) by default, but you can increase them
to represent horizontal or vertical spanning. The sizes cannot be null.

.. doctest:: cell_demo
    :hide:

    >>> from benker.coord import Coord
    >>> from benker.box import Box
    >>> from benker.cell import Cell

To instantiate a :class:`~benker.cell.Cell`, you can do:

.. doctest:: box_demo

    >>> c1 = Cell("c1")
    >>> c2 = Cell("c2", styles={'color': 'red'})
    >>> c3 = Cell("c3", type="footer")
    >>> c4 = Cell("c4", width=2)
    >>> c5 = Cell("c5", height=2)

The string representation of a cell is the string representation of it's content:

.. doctest:: box_demo

    >>> for cell in c1, c2, c3, c4, c5:
    ...     print(cell)
    c1
    c2
    c3
    c4
    c5

On initialization, the cell min position is always (1, 1), a.k.a. the top-left.

.. doctest:: box_demo

    >>> c1 = Cell("c1")
    >>> c1.min
    Coord(x=1, y=1)
    >>> c1.size
    Size(width=1, height=1)
    >>> c1.box
    Box(min=Coord(x=1, y=1), max=Coord(x=1, y=1))

A cell can be moved to another position:

.. doctest:: box_demo

    >>> c1 = Cell("c1", width=3, height=2)
    >>> c2 = c1.move_to(Coord(5, 3))
    >>> c2.min
    Coord(x=5, y=3)
    >>> c2.size
    Size(width=3, height=2)
    >>> c2.box
    Box(min=Coord(x=5, y=3), max=Coord(x=7, y=4))

You can check if a coord is inside the box:

.. doctest:: box_demo

    >>> c1 = Cell("c1", width=3, height=2)
    >>> c2 = c1.move_to(Coord(5, 3))
    >>> (7, 4) in c2
    True
    >>> Coord(6, 3) in c2
    True
    >>> Box(6, 3, 7, 4) in c2
    True

"""
import functools

from benker.box import Box


@functools.total_ordering
class Cell(object):
    """
    A cell is a box with a *content*.
    """

    def __init__(self, content, styles=None, type="body", x=1, y=1, width=1, height=1):
        self.content = content
        self.styles = styles
        self.type = type
        self._box = Box(x, y, x + width - 1, y + height - 1)

    def __str__(self):
        return str(self.content)

    def __repr__(self):
        cls = self.__class__.__name__
        return ("<{cls}({self.content!r}, "
                "styles={self.styles!r}, "
                "type={self.type!r}, "
                "x={self.min.x!r}, "
                "y={self.min.y!r}, "
                "width={self.width!r}, "
                "height={self.height!r})>"
                .format(cls=cls, self=self))

    @property
    def styles(self):
        return self._styles

    @styles.setter
    def styles(self, styles):
        # each cell owns it's own copy of the styles
        self._styles = {} if styles is None else styles.copy()

    @property
    def box(self):
        return self._box

    @property
    def min(self):
        return self.box.min

    @property
    def max(self):
        return self.box.max

    @property
    def size(self):
        return self.box.size

    @property
    def width(self):
        return self.box.width

    @property
    def height(self):
        return self.box.height

    # total ordering based on Box ordering

    def __lt__(self, other):
        if isinstance(other, Cell):
            return self.box < other.box
        elif isinstance(other, Box):
            return self.box < other
        return NotImplemented

    def __contains__(self, other):
        return other in self.box

    def transform(self, coord=None, size=None):
        box = self.box.transform(coord=coord, size=size)
        cell = Cell(self.content,
                    styles=self.styles,
                    type=self.type,
                    x=box.min.x,
                    y=box.min.y,
                    width=box.width,
                    height=box.height)
        return cell

    def move_to(self, coord):
        return self.transform(coord=coord)

    def resize(self, size):
        return self.transform(size=size)
