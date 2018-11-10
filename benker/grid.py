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
    >>> grid[2, 1] = Cell(content="pink", width=2)
    >>> grid[2, 2] = Cell(content="blue")

    >>> print(grid)
    +-----------+-----------------------+
    |    red    |   pink                |
    |           +-----------+-----------+
    |           |   blue    |           |
    +-----------+-----------+-----------+

You can retrieve the grid cells as follow:

.. doctest:: grid_demo

    >>> grid[1, 1]
    <Cell('red', styles={}, type='body', x=1, y=1, width=1, height=2)>
    >>> grid[2, 1]
    <Cell('pink', styles={}, type='body', x=2, y=1, width=2, height=1)>
    >>> grid[2, 2]
    <Cell('blue', styles={}, type='body', x=2, y=2, width=1, height=1)>
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
    <Cell('blue', styles={}, type='body', x=2, y=2, width=2, height=1)>
    >>> print(grid)
    +-----------+-----------------------+
    |    red    |   pink                |
    |           +-----------------------+
    |           |   blue                |
    +-----------+-----------------------+

The content of the merged cells is merged too:

    >>> grid.merge((2, 1), (3, 2), content_appender=lambda a, b: "/".join([a, b]))
    <Cell('pink/blue', styles={}, type='body', x=2, y=1, width=2, height=2)>
    >>> print(grid)
    +-----------+-----------------------+
    |    red    | pink/blue             |
    |           |                       |
    |           |                       |
    +-----------+-----------------------+
"""
import bisect
import collections
import operator

from benker.box import Box
from benker.coord import Coord
from benker.drawing import draw
from benker.size import Size


def _get_coord(coord):
    coord_type = type(coord)
    if coord_type is Coord:
        return coord
    elif coord_type is tuple and tuple(map(type, coord)) == (int, int):
        return Coord(*coord)
    raise TypeError(repr(coord_type))


class Grid(collections.MutableMapping):
    def __init__(self, cells=None):
        # fixme: verigier les cells (disjointes)
        self._cells = [] if cells is None else sorted(cells)

    def __contains__(self, coord):
        # fixme: algo fifferent is Box car tenir compose de box.min et box.max
        coord = _get_coord(coord)
        return any(coord in cell for cell in self._cells)

    def __getitem__(self, coord):
        coord = _get_coord(coord)
        for cell in self._cells:
            if coord in cell:
                return cell
        raise KeyError(coord)

    def __delitem__(self, coord):
        coord = _get_coord(coord)
        for cell in self._cells[:]:
            if coord in cell:
                self._cells.remove(cell)
                return
        raise KeyError(coord)

    def __setitem__(self, coord, new_cell):
        coord = _get_coord(coord)  # type: Coord
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
        if len(self):
            boxes = [cell.box for cell in self._cells]
            bounding_box = boxes[0].union(*boxes[1:])
            return bounding_box
        raise ValueError("grid is empty")

    def merge(self, start, end, content_appender=None):
        start_coord = _get_coord(start)
        end_coord = _get_coord(end)
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
