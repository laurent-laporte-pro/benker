# coding: utf-8
"""
Grid
====

A grid of cells.

.. doctest:: grid_demo
    :hide:

    >>> from benker.cell import Cell
    >>> from benker.point import Point
    >>> from benker.box import Box

Example of grid::

.. doctest:: grid_demo

    >>> from benker.grid import Grid

    >>> grid = Grid()
    >>> grid[1, 1] = Cell("A1:A2", height=2)
    >>> grid[2, 1] = Cell(content="B1:C1", width=2)
    >>> grid[2, 2] = Cell(content="B2")

    >>> print(grid)
    +-----------+-----------------------+
    |   A1:A2   |   B1:C1               |
    |           +-----------+-----------+
    |           |    B2     |           |
    +-----------+-----------+-----------+

You can retrieve the grid cells as follow:

.. doctest:: grid_demo

    >>> grid[1, 1]
    <Cell('A1:A2', styles={}, type='body', width=1, height=2)>
    >>> grid[2, 1]
    <Cell('B1:C1', styles={}, type='body', width=2, height=1)>
    >>> grid[2, 2]
    <Cell('B2', styles={}, type='body', width=1, height=1)>
    >>> grid[3, 3]
    Traceback (most recent call last):
        ...
    KeyError: (3, 3)

A grid has a bounding box, useful to get the grid dimensions:

    >>> grid.bounding_box
    Box(min=Point(x=1, y=1), max=Point(x=3, y=2))
    >>> grid.bounding_box.dimension
    Point(x=3, y=2)

You can expand the cell size horizontally or vertically:

    >>> grid.expand((2, 2), width=1)
    <Cell('B2', styles={}, type='body', width=2, height=1)>
    >>> print(grid)
    +-----------+-----------------------+
    |   A1:A2   |   B1:C1               |
    |           +-----------------------+
    |           |    B2                 |
    +-----------+-----------------------+

The content of the merged cells is merged too:

    >>> grid.merge((2, 1), (3, 2))
    <Cell('B1:C1B2', styles={}, type='body', width=2, height=2)>
    >>> print(grid)
    +-----------+-----------------------+
    |   A1:A2   |  B1:C1B2              |
    |           |                       |
    |           |                       |
    +-----------+-----------------------+
"""
import bisect
import collections
import operator

from benker.box import Box
from benker.drawing import draw
from benker.point import Point


def _get_point(coord):
    types = tuple(map(type, coord))
    if types == (int, int):
        min_x, min_y = coord
    elif types == (Point,):
        min_x, min_y = coord[0]
    elif types == (Box,):
        min_x, min_y = coord.min
    else:
        raise TypeError(repr(types))
    return Point(min_x, min_y)


class Grid(collections.MutableMapping):
    def __init__(self, cells=None):
        self._cells = [] if cells is None else sorted(cells)

    def __contains__(self, coord):
        point = _get_point(coord)
        return any(point in cell for cell in self._cells)

    def __getitem__(self, coord):
        point = _get_point(coord)
        for cell in self._cells:
            if point in cell:
                return cell
        raise KeyError(coord)

    def __delitem__(self, coord):
        point = _get_point(coord)
        for cell in self._cells[:]:
            if point in cell:
                self._cells.remove(cell)
                return
        raise KeyError(coord)

    def __setitem__(self, coord, new_cell):
        point = _get_point(coord)  # type: Point
        new_cell = new_cell.move_to(point)
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
        start_pt = _get_point(start)
        end_pt = _get_point(end)
        content_appender = content_appender or operator.__add__
        new_box = Box(start_pt, end_pt)
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
        new_cell = first.transform(target=new_box.min, dimension=new_box.dimension)
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
        end = Point(box.max.x + width, box.max.y + height)
        return self.merge(start, end, content_appender=content_appender)
