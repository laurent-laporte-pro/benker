# coding: utf-8
"""
Grid
====

A grid of cells.

Example of grid::

.. doctest:: grid_demo

    >>> from benker.grid import Grid
    >>> from benker.cell import Cell

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

    >>> from benker.grid import Grid
    >>> from benker.cell import Cell

    >>> grid = Grid()
    >>> grid[1, 1] = Cell("red", height=2)
    >>> grid[2, 1] = Cell("pink", width=2)
    >>> grid[2, 2] = Cell("blue")

    >>> grid[1, 1]
    <Cell('red', styles={}, nature='body', x=1, y=1, width=1, height=2)>
    >>> grid[2, 1]
    <Cell('pink', styles={}, nature='body', x=2, y=1, width=2, height=1)>
    >>> grid[2, 2]
    <Cell('blue', styles={}, nature='body', x=2, y=2, width=1, height=1)>
    >>> grid[3, 3]
    Traceback (most recent call last):
        ...
    KeyError: Coord(x=3, y=3)

A grid has a bounding box, useful to get the grid sizes:

.. doctest:: grid_demo

    >>> from benker.grid import Grid
    >>> from benker.cell import Cell

    >>> grid = Grid()
    >>> grid[1, 1] = Cell("red", height=2)
    >>> grid[2, 1] = Cell("pink", width=2)
    >>> grid[2, 2] = Cell("blue")

    >>> grid.bounding_box
    Box(min=Coord(x=1, y=1), max=Coord(x=3, y=2))
    >>> grid.bounding_box.size
    Size(width=3, height=2)

You can expand the cell size horizontally or vertically:

.. doctest:: grid_demo

    >>> from benker.grid import Grid
    >>> from benker.cell import Cell

    >>> grid = Grid()
    >>> grid[1, 1] = Cell("red", height=2)
    >>> grid[2, 1] = Cell("pink", width=2)
    >>> grid[2, 2] = Cell("blue")

    >>> grid.expand((2, 2), width=1)
    <Cell('blue', styles={}, nature='body', x=2, y=2, width=2, height=1)>
    >>> print(grid)
    +-----------+-----------------------+
    |    red    |   pink                |
    |           +-----------------------+
    |           |   blue                |
    +-----------+-----------------------+

The content of the merged cells is merged too:

.. doctest:: grid_demo

    >>> from benker.grid import Grid
    >>> from benker.cell import Cell

    >>> grid = Grid()
    >>> grid[1, 1] = Cell("red", height=2)
    >>> grid[2, 1] = Cell("pink", width=2)
    >>> grid[2, 2] = Cell("blue", width=2)

    >>> grid.merge((2, 1), (3, 2), content_appender=lambda a, b: "/".join([a, b]))
    <Cell('pink/blue', styles={}, nature='body', x=2, y=1, width=2, height=2)>
    >>> print(grid)
    +-----------+-----------------------+
    |    red    | pink/blue             |
    |           |                       |
    |           |                       |
    +-----------+-----------------------+
"""
import bisect
import itertools
import operator

try:
    from collections.abc import MutableMapping
except ImportError:
    from collections import MutableMapping

from benker.box import Box
from benker.coord import Coord
from benker.drawing import draw
from benker.size import Size


class Grid(MutableMapping):
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

    def __len__(self):
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
        """
        Merge a group of cells contained in a bounding box,
        using the *content_appender* to append cell contents.

        The coordinates *start* and *end* delimit a group of cells to merge.

        .. warning::

           All the cells of the group must be included in the group bounding box,
           no intersection is allowed. If not, :class:`ValueError` is raised.

        See also the method :meth:`~benker.grid.Grid.expand`
        to expand (or shrink) the width and/or height of a cell.

        :type  start: Coord or tuple[int, int]
        :param start:
            Top-left coordinates of the group of cells to merge.

        :type  start: Coord or tuple[int, int]
        :param end:
            Bottom-right coordinates of the group of cells to merge (inclusive).

        :param content_appender:
            Function to use to append the cell contents.
            The function must have the following signature: ``f(a, b) -> c``,
            where *a*, *b* anc *c* must be of the same type than the cell content.
            If not provided, the default function is :func:`operator.__add__`.

        :return: The merged cell.

        :raises ValueError:
            If the group of cells is empty or if cells cannot be merged.
        """
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
            if new_cell.content is None:
                new_cell.content = cell.content
            elif cell.content is None:
                pass  # no change
            else:
                new_cell.content = content_appender(new_cell.content, cell.content)
            new_cell.styles.update(cell.styles)
        self._cells = unchanged_cells
        boxes = [cell.box for cell in self._cells]
        index = bisect.bisect_left(boxes, Box(new_cell.box.min))
        self._cells.insert(index, new_cell)
        return new_cell

    def expand(self, coord, width=0, height=0, content_appender=None):
        """
        Expand (or shrink) the *width* and/or *height* of a cell,
        using the *content_appender* to append cell contents.

        See also the method :meth:`~benker.grid.Grid.merge`
        to merge a group of cells contained in a bounding box.

        :param coord:
            Coordinates of the cell to expand (or shrink).

        :param width:
            Number of columns to add to the cell width.

        :param height:
            Number of rows to add to the cell height.

        :param content_appender:
            Function to use to append the cell contents.
            The function must have the following signature: ``f(a, b) -> c``,
            where *a*, *b* anc *c* must be of the same type than the cell content.
            If not provided, the default function is :func:`operator.__add__`.

        :return: The merged cell.

        :raises ValueError:
            If the group of cells is empty or if cells cannot be merged.
        """
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
