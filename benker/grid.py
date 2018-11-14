# coding: utf-8
"""
Grid
====

A grid of cells.

.. doctest:: grid_demo
    :hide:

    >>> from benker.cell import Cell
    >>> from benker.coord import Coord
    >>> from benker.box import Box

Example of grid::

.. doctest:: grid_demo

    >>> from benker.grid import Grid

    >>> grid = Grid()
    >>> grid[1, 1] = Cell("red", height=2)
    >>> grid[2, 1] = Cell("pink", width=2)
    >>> grid[2, 2] = Cell("blue")

    >>> print(grid)
    +-----------+-----------------------+
    |    red    |   pink                |
    |           +-----------+-----------+
    |           |   blue    |           |
    +-----------+-----------+-----------+

You can retrieve the grid cells as follow:

.. doctest:: grid_demo

    >>> grid[1, 1]
    <Cell('red', styles={}, cell_group='body', x=1, y=1, width=1, height=2)>
    >>> grid[2, 1]
    <Cell('pink', styles={}, cell_group='body', x=2, y=1, width=2, height=1)>
    >>> grid[2, 2]
    <Cell('blue', styles={}, cell_group='body', x=2, y=2, width=1, height=1)>
    >>> grid[3, 3]
    Traceback (most recent call last):
        ...
    KeyError: Coord(x=3, y=3)

A grid has a bounding box, useful to get the grid sizes:

    >>> grid.bounding_box
    Box(min=Coord(x=1, y=1), max=Coord(x=3, y=2))
    >>> grid.bounding_box.size
    Size(width=3, height=2)

You can expand the cell size horizontally or vertically:

    >>> grid.expand((2, 2), width=1)
    <Cell('blue', styles={}, cell_group='body', x=2, y=2, width=2, height=1)>
    >>> print(grid)
    +-----------+-----------------------+
    |    red    |   pink                |
    |           +-----------------------+
    |           |   blue                |
    +-----------+-----------------------+

The content of the merged cells is merged too:

    >>> grid.merge((2, 1), (3, 2), content_appender=lambda a, b: "/".join([a, b]))
    <Cell('pink/blue', styles={}, cell_group='body', x=2, y=1, width=2, height=2)>
    >>> print(grid)
    +-----------+-----------------------+
    |    red    | pink/blue             |
    |           |                       |
    |           |                       |
    +-----------+-----------------------+
"""
import bisect
import collections
import itertools
import operator

from benker.box import Box
from benker.coord import Coord
from benker.drawing import draw
from benker.size import Size


class Grid(collections.MutableMapping):
    """
    Collection of :class:`~benker.cell.Cell` objects ordered in a grid of rows and columns.
    """
    __slots__ = ('_cells',)

    def __init__(self, cells=None):
        """
        Construct a grid from an iterable of cells.
        All cells must be disjoints.

        Cells are ordered according to the total ordering of the cell boxes.

        :type  cells: typing.Iterable[benker.cell.Cell]
        :param cells: Collection of cells.

        :raises KeyError: if at least one cell intersect another one.
        """
        self._cells = []
        cells = cells or []
        for cell in cells:
            self.__setitem__(cell.min, cell)

    def __repr__(self):
        cls = self.__class__.__name__
        return "{cls}({cells!r})".format(cls=cls, cells=self._cells)

    def __contains__(self, coord):
        coord = Coord.from_value(coord)
        return any(coord in cell for cell in self._cells)

    def __getitem__(self, coord):
        coord = Coord.from_value(coord)
        for cell in self._cells:
            if coord in cell:
                return cell
        raise KeyError(coord)

    def __delitem__(self, coord):
        coord = Coord.from_value(coord)
        for cell in self._cells[:]:
            if coord in cell:
                self._cells.remove(cell)
                return
        raise KeyError(coord)

    def __setitem__(self, coord, new_cell):
        coord = Coord.from_value(coord)  # type: Coord
        new_cell = new_cell.move_to(coord)
        for cell in self._cells[:]:
            if cell.box.intersect(new_cell.box):
                raise KeyError(coord)
        boxes = [cell.box for cell in self._cells]
        index = bisect.bisect_left(boxes, Box(new_cell.box.min))
        self._cells.insert(index, new_cell)

    def __len__(self) -> int:
        return len(self._cells)

    def __iter__(self):
        return iter(self._cells)

    def __str__(self):
        return draw(self)

    @property
    def bounding_box(self):
        """ Bounding box of the grid (``None`` if the grid is empty). """
        if len(self):
            boxes = [cell.box for cell in self._cells]
            bounding_box = boxes[0].union(*boxes[1:])
            return bounding_box
        return None

    def merge(self, start, end, content_appender=None):
        start_coord = Coord.from_value(start)
        end_coord = Coord.from_value(end)
        content_appender = content_appender or operator.__add__
        new_box = Box(start_coord, end_coord)
        merged_cells = []
        unchanged_cells = []
        for cell in self._cells:
            if cell.box in new_box:
                merged_cells.append(cell)
            elif cell.box.intersect(new_box):
                raise ValueError((start, end))
            else:
                unchanged_cells.append(cell)
        if not merged_cells:
            # nothing to merge
            raise ValueError((start, end))
        first = merged_cells.pop(0)
        new_cell = first.transform(coord=new_box.min, size=new_box.size)
        for cell in merged_cells:
            new_cell.content = content_appender(new_cell.content, cell.content)
            new_cell.styles.update(cell.styles)
        self._cells = unchanged_cells
        boxes = [cell.box for cell in self._cells]
        index = bisect.bisect_left(boxes, Box(new_cell.box.min))
        self._cells.insert(index, new_cell)
        return new_cell

    def expand(self, coord, width=0, height=0, content_appender=None):
        content_appender = content_appender or operator.__add__
        box = self[coord].box
        start = box.min
        end = box.max + Size(width, height)
        return self.merge(start, end, content_appender=content_appender)

    def iter_rows(self):
        """ Iterate the cells grouped by rows. """
        cells = self._cells
        for group, cells in itertools.groupby(cells, key=lambda c: c.min.y):
            yield tuple(cells)
