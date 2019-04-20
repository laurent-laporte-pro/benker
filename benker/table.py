# coding: utf-8
"""
Table
=====

Generic table structure which simplify the conversion from docx table format to CALS or HTML tables.
"""
import re

try:
    from collections.abc import MutableMapping
except ImportError:
    from collections import MutableMapping

from benker.cell import Cell
from benker.coord import Coord
from benker.grid import Grid
from benker.styled import Styled


# noinspection PyUnresolvedReferences
class TableViewList(object):
    """
    This class defined a (simplified) list of views.

    Short demonstration:

    .. doctest:: table_demo

        >>> from benker.cell import Cell
        >>> from benker.table import Table
        >>> from benker.table import ColView
        >>> from benker.table import RowView
        >>> from benker.table import TableViewList

        >>> red = Cell('red', x=1, y=1, height=2)
        >>> pink = Cell('pink', x=2, y=1, width=2)
        >>> blue = Cell('blue', x=2, y=2)
        >>> table = Table([red, pink, blue])
        >>> print(table)
        +-----------+-----------------------+
        |    red    |   pink                |
        |           +-----------+-----------+
        |           |   blue    |           |
        +-----------+-----------+-----------+

        >>> cols = TableViewList(table, ColView)
        >>> len(cols)
        3
        >>> rows = TableViewList(table, RowView)
        >>> len(rows)
        2

        >>> for pos, col in enumerate(cols, 1):
        ...     print("col #{pos}: {col}".format(pos=pos, col=str(col)))
        col #1: [red]
        col #2: [pink, blue]
        col #3: []

        >>> cols[3].insert_cell("yellow")
        >>> print(table)
        +-----------+-----------------------+
        |    red    |   pink                |
        |           +-----------+-----------+
        |           |   blue    |  yellow   |
        +-----------+-----------+-----------+
    """

    def __init__(self, table, view_cls):
        """
        Construct a list of view attached to the given *table*.

        :type  table: benker.table.Table
        :param table: Reference to the table.

        :type  view_cls: type
        :param view_cls:
            A view class, either :class:`~benker.table.RowView` or :class:`~benker.table.ColView`.
        """
        self.table = table
        self.view_cls = view_cls
        self.views = []
        self.refresh_all()

    def adopt_cell(self, cell):
        """
        Adopt a new cell in the views.

        :type  cell: benker.cell.Cell
        :param cell: New cell to adopt
        """
        views = self.views
        box = cell.box
        if self.view_cls is RowView:
            self._fit_to_size(box.max.y, truncate=False)
            for pos in range(box.min.y, box.max.y + 1):
                views[pos - 1].adopt_cell(cell)
        elif self.view_cls is ColView:
            self._fit_to_size(box.max.x, truncate=False)
            for pos in range(box.min.x, box.max.x + 1):
                views[pos - 1].adopt_cell(cell)
        else:
            raise TypeError(repr(self.view_cls))

    def refresh_all(self):
        """
        Cleanup and refresh all the views, taking into account the cells
        which are in the table grid.
        """
        views = self.views
        bounding_box = self.table.bounding_box
        if bounding_box is None:
            views[:] = []
            return

        if self.view_cls is RowView:
            self._fit_to_size(bounding_box.max.y)
        elif self.view_cls is ColView:
            self._fit_to_size(bounding_box.max.x)
        else:
            raise TypeError(repr(self.view_cls))

        for view in views:
            view.owned_cells[:] = []
            view.caught_cells[:] = []

        for cell in self.table:
            self.adopt_cell(cell)

    def _fit_to_size(self, size, truncate=True):
        views = self.views
        if truncate:
            del views[size:]
        for index in range(len(views), size):
            views.append(self.view_cls(self.table, index + 1))

    def __getitem__(self, pos):
        self._fit_to_size(pos, truncate=False)
        return self.views[pos - 1]

    def __len__(self):
        return len(self.views)

    def __iter__(self):
        return iter(self.views)


def _camel_to_snake(camel_name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', camel_name)
    snake_name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    return snake_name


class ViewsProperty(object):
    """
    Descriptor used to define the rows/cols properties
    in the class :class:`~benker.table.Table`.
    """

    def __init__(self, view_cls):
        """
        Construct a "Views" property which handles a list of items which type is *view_cls*.

        :type  view_cls: type
        :param view_cls:
            A view class, either :class:`~benker.table.RowView` or :class:`~benker.table.ColView`.
        """
        self.view_cls = view_cls
        # CamelCase to snake_case:
        cls_module = self.view_cls.__module__
        cls_name = self.view_cls.__name__
        self.attr_name = "_{}".format(_camel_to_snake(cls_name))
        self.__doc__ = "List of views of type :class:`~{0}.{1}`".format(cls_module, cls_name)

    def __get__(self, table, owner):
        if table is None:
            return self
        if not hasattr(table, self.attr_name):
            setattr(table, self.attr_name, TableViewList(table, self.view_cls))
        return getattr(table, self.attr_name)


class TableView(Styled):
    """
    Base class of :class:`~benker.table.RowView` and :class:`~benker.table.ColView`
    used to create a view on the table cells for a given row or column.

    See also: :class:`~benker.table.TableViewList`
    """
    __slots__ = ('_table', '_pos', '_owned_cells', '_caught_cells')

    def __init__(self, table, pos, styles=None, nature="body"):
        """
        Initialize a row/column view.

        :type  table: benker.table.Table
        :param table: Reference to the table which contains the cells to "view".

        :param int pos:
            Row or column pos (1-based) used to select cells.

        :type  styles: typing.Dict[str, str]
        :param styles:
            Dictionary of key-value pairs, where *keys* are the style names.

        :param str nature:
            Cell *nature* used to distinguish the body cells, from the header and the footer.
            The default value is "body", but you can use "header", "footer" or whatever
            is suitable for your needs.
        """
        super(TableView, self).__init__(styles, nature)
        self._table = table
        self._pos = pos
        self._owned_cells = []
        self._caught_cells = []

    def __str__(self):
        items = ", ".join(str(cell) for cell in self._owned_cells)
        return "[{0}]".format(items)

    @property
    def table(self):
        """ Non-mutable reference to the table (instance of :class:`~benker.table.Table`). """
        return self._table

    @property
    def owned_cells(self):
        """ List of cells owned by this view. """
        return self._owned_cells

    @property
    def caught_cells(self):
        """ List of cells caught (intercepted) by this view. """
        return self._caught_cells

    def can_own(self, cell):
        """
        Check if a cell can be stored it that view.

        :type  cell: benker.cell.Cell
        :param cell: table cell
        :return: ``True`` if the cell belong to this view.
        """
        raise NotImplementedError

    def can_catch(self, cell):
        """
        Check if a cell can be caught by that view.

        :type  cell: benker.cell.Cell
        :param cell: table cell
        :return: ``True`` if the cell intercept to this view.
        """
        raise NotImplementedError

    def adopt_cell(self, cell):
        """
        Event handler called by the system when
        a cell is about to be inserted in the table.
        """
        if self.can_own(cell):
            self._owned_cells.append(cell)
        if self.can_catch(cell):
            self._caught_cells.append(cell)


class RowView(TableView):
    """
    A view on the table cells for a given row.
    """

    def can_own(self, cell):
        return cell.min.y == self._pos

    def can_catch(self, cell):
        return Coord(cell.min.x, self._pos) in cell

    @property
    def row_pos(self):
        """ Row position in the table (1-based). """
        return self._pos

    def insert_cell(self, content, styles=None, nature='body', width=1, height=1):
        """
        Insert a new cell in the row at the next free position, or at the end.

        :param content:
            User-defined cell content. It can be of any type: ``None``,
            :class:`str`, :class:`int`, :class:`float`, a container (:class:`list`),
            a XML element, etc. The same content can be shared by several cells, it's
            your own responsibility to handle the copy (or deep copy) of the *content*
            reference when needed.

        :type  styles: typing.Dict[str, str]
        :param styles:
            User-defined cell styles: a dictionary of key-value pairs.
            This values are useful to store some HTML-like styles (border-style,
            border-width, border-color, vertical-align, text-align, etc.).
            Of course, we are not tied to the HTML-like styles, you can use your own
            list of styles.

        :type nature: str
        :ivar nature: nature: a way to distinguish the body cells, from the header and the footer.
            The default value is "body", but you can use "header", "footer" or whatever
            is suitable for your needs.

        :param int width:
            Width of the cell (columns spanning), default to 1.

        :param int height:
            Height of the cell (rows spanning), default to 1.
        """
        caught_cells = self._caught_cells
        y = self._pos
        if caught_cells:
            boxes = tuple(cell.box for cell in caught_cells)
            bounding_box = boxes[0].union(*boxes[1:])
            for x in range(1, bounding_box.max.x + 1):
                if all((x, y) not in box for box in boxes):
                    break
            else:
                x = bounding_box.max.x + 1
        else:
            x = 1
        cell = Cell(content, styles=styles, nature=nature,
                    x=x, y=y, width=width, height=height)
        self._table[cell.min] = cell


class ColView(TableView):
    """
    A view on the table cells for a given column.
    """

    def can_own(self, cell):
        return cell.min.x == self._pos

    def can_catch(self, cell):
        return Coord(self._pos, cell.min.y) in cell

    @property
    def col_pos(self):
        """ Column position in the table (1-based). """
        return self._pos

    def insert_cell(self, content, styles=None, nature=None, width=1, height=1):
        """
        Insert a new cell in the column at the next free position, or at the end.

        :param content:
            User-defined cell content. It can be of any type: ``None``,
            :class:`str`, :class:`int`, :class:`float`, a container (:class:`list`),
            a XML element, etc. The same content can be shared by several cells, it's
            your own responsibility to handle the copy (or deep copy) of the *content*
            reference when needed.

        :type  styles: typing.Dict[str, str]
        :param styles:
            User-defined cell styles: a dictionary of key-value pairs.
            This values are useful to store some HTML-like styles (border-style,
            border-width, border-color, vertical-align, text-align, etc.).
            Of course, we are not tied to the HTML-like styles, you can use your own
            list of styles.

        :type nature: str
        :ivar nature: nature: a way to distinguish the body cells, from the header and the footer.
            The default value is "body", but you can use "header", "footer" or whatever
            is suitable for your needs.

        :param int width:
            Width of the cell (columns spanning), default to 1.

        :param int height:
            Height of the cell (rows spanning), default to 1.
        """
        caught_cells = self._caught_cells
        x = self._pos
        if caught_cells:
            boxes = tuple(cell.box for cell in caught_cells)
            bounding_box = boxes[0].union(*boxes[1:])
            for y in range(1, bounding_box.max.y + 1):
                if all((x, y) not in box for box in boxes):
                    break
            else:
                y = bounding_box.max.y + 1
        else:
            y = 1
        cell = Cell(content, styles=styles, nature=nature,
                    x=x, y=y, width=width, height=height)
        self._table[cell.min] = cell


class Table(Styled, MutableMapping):
    """
    Table data structure used to simplify conversion to CALS or HTML.

    Short demonstration:

    .. doctest:: table_demo

        >>> from benker.cell import Cell
        >>> from benker.table import Table

        >>> table = Table(styles={'frame': 'all'})

        >>> table[(1, 1)] = Cell("one")
        >>> table.rows[1].insert_cell("two")

        >>> table[(2, 1)]
        <Cell('two', styles={}, nature='body', x=2, y=1, width=1, height=1)>

        >>> table.cols[1].insert_cell("alpha")
        >>> table.cols[2].insert_cell("beta")
        >>> (1, 2) in table
        True

        >>> del table[(1, 2)]
        >>> (1, 2) in table
        False

        >>> len(table)
        3

        >>> for cell in table:
        ...     print(cell)
        one
        two
        beta

        >>> for row in table.rows:
        ...     print(row)
        [one, two]
        [beta]

        >>> table.merge((1, 2), (2, 2))
        >>> print(table)
        +-----------+-----------+
        |    one    |    two    |
        +-----------------------+
        |   beta                |
        +-----------------------+

        >>> table.expand((1, 1), width=3)
        >>> print(table)
        +-----------------------------------------------+
        |              onetwo                           |
        +-----------------------+-----------+-----------+
        |   beta                |           |           |
        +-----------------------+-----------+-----------+

    :type styles: typing.Dict[str, str]
    :ivar styles:
        User-defined table styles: a dictionary of key-value pairs.
        This values are useful to store some HTML-like styles (border-style,
        border-width, border-color, vertical-align, text-align, etc.).
        Of course, we are not tied to the HTML-like styles, you can use your own
        list of styles.

        .. note::

            The style dictionary is always copied: in other words, key-value pairs
            are copied but a shallow copy is done for the values (in general, it
            is not a problem if you use non-mutable values like :class:`str`).

    :type nature: str
    :ivar nature:
        A table can have a nature: a way to distinguish the body cells,
        from the header and the footer. The default value is "body", but you can
        use "header", "footer" or whatever is suitable for your needs.
        This kind of information is in general not stored in the styles,
        even if it is similar.

        .. note::

            In a :class:`~benker.grid.Grid`, the :ref:`merging <benker__grid__merging>`
            of two natures is done by keeping the first nature and
            dropping the second one. In other words, the resulting nature is
            the group of the most top-left nature of the merged cells.
    """

    rows = ViewsProperty(RowView)
    cols = ViewsProperty(ColView)

    def __init__(self, cells=None, styles=None, nature=None):
        """
        Construct a table object from a collection of cells and a dictionary of styles.

        :type  cells: typing.Iterable[benker.cell.Cell]
        :param cells: Collection of cells.

        :type  styles: typing.Dict[str, str]
        :param styles:
            Dictionary of key-value pairs, where *keys* are the style names.

        :type nature: str
        :ivar nature:
            User-defined string value.
            Table *nature* is similar to HTML ``@class`` attribute,
            you can use it do identify the styles to apply to your table.
        """
        super(Table, self).__init__(styles, nature)
        self._grid = Grid(cells)

    def __str__(self):
        return str(self._grid)

    @property
    def bounding_box(self):
        """
        Bounding box of the table (``None`` if the table is empty).

        :rtype: benker.box.Box
        :return: The bounding box.
        """
        return self._grid.bounding_box

    def _refresh_views(self, cell=None):
        """
        Refresh all the rows and column views.
        """
        if cell:
            self.rows.adopt_cell(cell)
            self.cols.adopt_cell(cell)
        else:
            self.rows.refresh_all()
            self.cols.refresh_all()

    def __contains__(self, coord):
        """
        Check if the table contains a cell (a owned cell) at the given coordinates.

        :type  coord: Coord or tuple(int, int)
        :param coord: Coordinates in the tables (1-indexed).

        :return: ``True`` if the table contains a cell at the given
            coordinates, else ``False``.
        """
        return coord in self._grid

    def __setitem__(self, coord, cell):
        """
        Insert a cell in the table at the given coordinates.

        :type  coord: Coord or tuple(int, int)
        :param coord: Coordinates in the tables (1-indexed).

        :type  cell: benker.cell.Cell
        :param cell: Cell to insert.
        """
        self._grid[coord] = cell
        # get the cell with its new coordinates:
        cell = self._grid[coord]
        self._refresh_views(cell)

    def __delitem__(self, coord):
        """
        Delete a cell from the table at the given coordinates.

        :type  coord: Coord or tuple(int, int)
        :param coord: Coordinates in the tables (1-indexed).
        """
        del self._grid[coord]
        self._refresh_views()

    def __getitem__(self, coord):
        """
        Get a cell at the given coordinates.

        :type  coord: Coord or tuple(int, int)
        :param coord: Coordinates in the tables (1-indexed).

        :rtype: benker.cell.Cell
        :return: The cell.
        """
        return self._grid[coord]

    def __len__(self):
        return len(self._grid)

    def __iter__(self):
        return iter(self._grid)

    def merge(self, start, end, content_appender=None):
        self._grid.merge(start, end, content_appender=content_appender)
        self._refresh_views()

    def expand(self, coord, width=0, height=0, content_appender=None):
        self._grid.expand(coord, width=width, height=height, content_appender=content_appender)
        self._refresh_views()
