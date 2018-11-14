# coding: utf-8
"""
Table
=====

Generic table structure which simplify the conversion from docx table format to CALS or HTML tables.
"""
import re

from benker.cell import Cell
from benker.coord import Coord
from benker.grid import Grid
from benker.styled import Styled


class TableViewList(object):
    """
    This class defined a (simplified) list of views.

    Simple usage:

    .. doctest:: table_demo

        >>> from benker.cell import Cell
        >>> from benker.table import Table
        >>> from benker.table import ColView
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

        >>> for pos, col in enumerate(cols, 1):
        ...     print("col #{}: [".format(pos), end="")
        ...     print(", ".join(cell.content for cell in col.owned_cells), end="")
        ...     print("]")
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
        bounding_box = self.table.bounding_box
        if bounding_box:
            if self.view_cls == RowView:
                self._fit_to_size(bounding_box.height)
            elif self.view_cls == ColView:
                self._fit_to_size(bounding_box.width)
            else:
                raise TypeError(repr(self.view_cls))

    def _fit_to_size(self, size):
        for index in range(len(self.views), size):
            self.views.append(self.view_cls(self.table, index + 1, cell_group=self.table.cell_group))

    def __getitem__(self, pos):
        self._fit_to_size(pos)
        return self.views[pos - 1]

    def __len__(self):
        return len(self.views)

    def __iter__(self):
        return iter(self.views)


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
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', cls_name)
        name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
        self.attr_name = "_{}".format(name)
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

    def __init__(self, table, pos, styles=None, cell_group="body"):
        """
        Initialize a row/column view.

        :type  table: benker.table.Table
        :param table: Reference to the table which contains the cells to "view".

        :param int pos:
            Row or column pos (1-based) used to select cells.

        :type  styles: typing.Dict[str, str]
        :param styles:
            Dictionary of key-value pairs, where *keys* are the style names.

        :param str cell_group:
            Cell group: a way to distinguish the body cells, from the header and the footer.
            The default value is "body", but you can use "header", "footer" or whatever
            is suitable for your needs.
        """
        super(TableView, self).__init__(styles, cell_group)
        self._table = table
        self._pos = pos
        self._owned_cells = [cell for cell in table.iter_cells() if self.can_own(cell)]
        self._caught_cells = [cell for cell in table.iter_cells() if self.can_catch(cell)]

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

    def on_insert_cell(self, cell):
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

    def insert_cell(self, content, styles=None, width=1, height=1):
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
        cell = Cell(content, styles=styles, cell_group=self.cell_group,
                    x=x, y=y, width=width, height=height)
        self._table.on_insert_cell(cell)


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
        # type: () -> int
        return self._pos

    def insert_cell(self, content, styles=None, width=1, height=1):
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
        cell = Cell(content, styles=styles, cell_group=self.cell_group,
                    x=x, y=y, width=width, height=height)
        self._table.on_insert_cell(cell)


class Table(Styled):
    """
    Table data structure used to simplify conversion to CALS or HTML.

    :type  cells: typing.Iterable[benker.cell.Cell]
    :param cells: Collection of cells.

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

    :type cell_group: str
    :ivar cell_group:
        A table can have a cell group: a way to distinguish the body cells,
        from the header and the footer. The default value is "body", but you can
        use "header", "footer" or whatever is suitable for your needs.
        This kind of information is in general not stored in the styles,
        even if it is similar.

        .. note::

            In a :class:`~benker.grid.Grid`, the :ref:`merging <benker__grid__merging>`
            of two cell groups is done by keeping the first cell group and
            dropping the second one. In other words, the resulting cell group is
            the group of the most top-left cell group of the merged cells.
    """

    rows = ViewsProperty(RowView)
    cols = ViewsProperty(ColView)

    def __init__(self, cells=None, styles=None, cell_group="body"):
        super(Table, self).__init__(styles, cell_group)
        self._grid = Grid(cells)

    def __str__(self):
        return str(self._grid)

    @property
    def bounding_box(self):
        """ Bounding box of the table (``None`` if the table is empty). """
        return self._grid.bounding_box

    def iter_cells(self):
        return iter(self._grid)

    def iter_rows(self):
        return iter(self.rows)

    def iter_cols(self):
        return iter(self.cols)

    def on_insert_cell(self, cell):
        """
        Event handler called by the system when
        a cell is about to be inserted in the table.

        Dispatch the event to all the rows and columns.
        """
        self._grid[cell.min] = cell
        for row in self.rows:
            row.on_insert_cell(cell)
        for col in self.cols:
            col.on_insert_cell(cell)
