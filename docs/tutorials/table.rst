.. _benker__table:

Table
=====

.. _benker__table__description:

Description
-----------

A :class:`~benker.table.Table` is a data structure used to represent
Office Open XML tables, CALS tables or HTML tables.

A :class:`~benker.table.Table` is a :class:`~benker.styled.Styled` object,
so you can attach a dictionary of styles and a nature ("body" by default).
The nature is used to give a default value to the the row/column views.

.. doctest:: table

    >>> from benker.table import Table

    >>> Table(styles={'frame': 'all'})
    <Table({'frame': 'all'}, None)>

A table can be initialize with a collection of cells.
Make sure all cells are disjoints.

.. doctest:: table

    >>> from benker.cell import Cell

    >>> red = Cell('red', x=1, y=1, height=2)
    >>> pink = Cell('pink', x=2, y=1, width=2)
    >>> blue = Cell('blue', x=2, y=2)

    >>> table = Table([red, pink, blue], nature='header')
    >>> table
    <Table({}, 'header')>

    >>> print(table)
    +-----------+-----------------------+
    |    red    |   pink                |
    |           +-----------+-----------+
    |           |   blue    |           |
    +-----------+-----------+-----------+

.. warning::

    Make sure all cells are disjoints:

    .. doctest:: table

        >>> red = Cell('overlap', x=1, y=1, width=2)
        >>> pink = Cell('oops!', x=2, y=1)
        >>> Table([red, pink])
        Traceback (most recent call last):
            ...
        KeyError: Coord(x=2, y=1)

.. _benker__table__properties:

Properties
----------

You can use the following properties to extract information from a *table*:

The bounding box of a table is the bounding box of all cells in the grid:

.. doctest:: table

    >>> red = Cell('red', x=1, y=1, height=2)
    >>> pink = Cell('pink', x=2, y=1, width=2)
    >>> blue = Cell('blue', x=2, y=2)
    >>> table = Table([red, pink, blue])

    >>> table.bounding_box
    Box(min=Coord(x=1, y=1), max=Coord(x=3, y=2))

.. important::

    The bounding box is not defined for an empty table, so ``None`` is returned
    in that case (this behavior is preferable to raising an exception,
    in order to simplify interactive debugging).

    .. doctest:: table

        >>> table = Table()
        >>> table.bounding_box is None
        True


.. _benker__table__operations:

Operations
----------

.. _benker__table__insertion:

Cells Insertion
~~~~~~~~~~~~~~~

You can insert a row to a table. This row is then used to insert cells.

.. doctest:: table

    >>> table = Table()

    >>> row = table.rows[1]
    >>> row.nature = "header"
    >>> row.insert_cell("Astronomer", width=2)
    >>> row.insert_cell("Year")
    >>> row.insert_cell("Country")

    >>> row = table.rows[2]
    >>> row.insert_cell("Nicolaus")
    >>> row.insert_cell("Copernicus")
    >>> row.insert_cell("1473-1543")
    >>> row.insert_cell("Royal Prussia")

    >>> row = table.rows[3]
    >>> row.insert_cell("Charles")
    >>> row.insert_cell("Messier")
    >>> row.insert_cell("1730-1817")
    >>> row.insert_cell("France", height=2)

    >>> row = table.rows[4]
    >>> row.insert_cell("Jean-Baptiste")
    >>> row.insert_cell("Delambre")
    >>> row.insert_cell("1749-1822")

    >>> print(table)
    +-----------------------+-----------+-----------+
    | Astronome             |   Year    |  Country  |
    +-----------+-----------+-----------+-----------+
    | Nicolaus  | Copernicu | 1473-1543 | Royal Pru |
    +-----------+-----------+-----------+-----------+
    |  Charles  |  Messier  | 1730-1817 |  France   |
    +-----------+-----------+-----------|           |
    | Jean-Bapt | Delambre  | 1749-1822 |           |
    +-----------+-----------+-----------+-----------+

The *nature* of a cell is inherited from its parent's row.
The first row contains the header, so the cell nature is "header":

.. doctest:: table

    >>> table.rows[1].nature
    'header'
    >>> [cell.nature for cell in table.rows[1].owned_cells]
    ['header', 'header', 'header']

The other rows have no *nature*, so the cell nature is ``None``

.. doctest:: table

    >>> table.rows[2].nature is None
    True
    >>> all(cell.nature is None for cell in table.rows[2].owned_cells)
    True


.. _benker__table__merging:

Cells Merging
~~~~~~~~~~~~~

You can merge cells by giving the coordinates of the cells to merge
or by extending the size of a given cell.

.. doctest:: table

    >>> table = Table()
    >>> letters = "abcdEFGHijklMNOP"
    >>> for index, letter in enumerate(letters):
    ...     table[(1 + index % 4, 1 + index // 4)] = Cell(letter)
    >>> print(table)
    +-----------+-----------+-----------+-----------+
    |     a     |     b     |     c     |     d     |
    +-----------+-----------+-----------+-----------+
    |     E     |     F     |     G     |     H     |
    +-----------+-----------+-----------+-----------+
    |     i     |     j     |     k     |     l     |
    +-----------+-----------+-----------+-----------+
    |     M     |     N     |     O     |     P     |
    +-----------+-----------+-----------+-----------+

    >>> table.merge((2, 2), (3, 3))
    >>> print(table)
    +-----------+-----------+-----------+-----------+
    |     a     |     b     |     c     |     d     |
    +-----------+-----------------------+-----------+
    |     E     |   FGjk                |     H     |
    +-----------|                       +-----------+
    |     i     |                       |     l     |
    +-----------+-----------+-----------+-----------+
    |     M     |     N     |     O     |     P     |
    +-----------+-----------+-----------+-----------+

    >>> table.expand((2, 3), height=1)
    >>> print(table)
    +-----------+-----------+-----------+-----------+
    |     a     |     b     |     c     |     d     |
    +-----------+-----------------------+-----------+
    |     E     |                       |     H     |
    +-----------|                       +-----------+
    |     i     |  FGjkNO               |     l     |
    +-----------|                       +-----------+
    |     M     |                       |     P     |
    +-----------+-----------------------+-----------+

Owned and caught cells
~~~~~~~~~~~~~~~~~~~~~~

When a cell is merged into a row group, it is always bound to the top row of this group (the first row).
In that case, we say that the first row **owns** the cell and the other rows **catch** the cell.

.. doctest:: table

    >>> table = Table()

    >>> row = table.rows[1]
    >>> row.insert_cell("merged", height=2)
    >>> row.insert_cell("A")

    >>> row = table.rows[2]
    >>> row.insert_cell("B")

    >>> row = table.rows[3]
    >>> row.insert_cell("C")
    >>> row.insert_cell("D")
    >>> print(table)
    +-----------+-----------+
    |  merged   |     A     |
    |           +-----------+
    |           |     B     |
    +-----------+-----------+
    |     C     |     D     |
    +-----------+-----------+

Here are the **owned_cells** of this table:

.. doctest:: table

    >>> for pos, row in enumerate(table.rows, 1):
    ...     cells = ", ".join("{}".format(cell) for cell in row.owned_cells)
    ...     print("row #{pos}: {cells}".format(pos=pos, cells=cells))
    row #1: merged, A
    row #2: B
    row #3: C, D

Here are the **caught_cells** of this table:

.. doctest:: table

    >>> for pos, row in enumerate(table.rows, 1):
    ...     cells = ", ".join("{}".format(cell) for cell in row.caught_cells)
    ...     print("row #{pos}: {cells}".format(pos=pos, cells=cells))
    row #1: merged, A
    row #2: merged, B
    row #3: C, D

The same applies to columns: if a cell is merged into several columns then it belongs
to the first column (left) of the merged column group.

.. doctest:: table

    >>> table = Table()

    >>> row = table.rows[1]
    >>> row.insert_cell("merged", width=2)
    >>> row.insert_cell("A")

    >>> row = table.rows[2]
    >>> row.insert_cell("B")
    >>> row.insert_cell("C")
    >>> row.insert_cell("D")
    >>> print(table)
    +-----------------------+-----------+
    |  merged               |     A     |
    +-----------+-----------+-----------+
    |     B     |     C     |     D     |
    +-----------+-----------+-----------+

Here are the **owned_cells** of this table:

.. doctest:: table

    >>> for pos, col in enumerate(table.cols, 1):
    ...     cells = ", ".join("{}".format(cell) for cell in col.owned_cells)
    ...     print("col #{pos}: {cells}".format(pos=pos, cells=cells))
    col #1: merged, merged, B
    col #2: C
    col #3: A, D

Here are the **caught_cells** of this table:

.. doctest:: table

    >>> for pos, col in enumerate(table.cols, 1):
    ...     cells = ", ".join("{}".format(cell) for cell in col.caught_cells)
    ...     print("col #{pos}: {cells}".format(pos=pos, cells=cells))
    col #1: merged, merged, B
    col #2: merged, merged, C
    col #3: A, D

Fill missing cells
~~~~~~~~~~~~~~~~~~

When you build a table (from an uncontrolled source), you may have missing cells (holes).
For instance, in the table below, the cell C2 is missing:

.. doctest:: table

    >>> table = Table()
    >>> table.rows[1].insert_cell("one")
    >>> table.rows[1].insert_cell("two")
    >>> table.rows[1].insert_cell("three")
    >>> table.rows[1].insert_cell("four", height=2)
    >>> table.rows[2].insert_cell("un-deux", width=2)
    >>> print(table)
    +-----------+-----------+-----------+-----------+
    |    one    |    two    |   three   |   four    |
    +-----------------------+-----------|           |
    |  un-deux              |           |           |
    +-----------------------+-----------+-----------+

If you need to fill the missing cells, you can use the
:meth:`~benker.table.Table.fill_missing` method, like this:

.. doctest:: table

    >>> table.fill_missing("HERE")
    >>> print(table)
    +-----------+-----------+-----------+-----------+
    |    one    |    two    |   three   |   four    |
    +-----------------------+-----------|           |
    |  un-deux              |   HERE    |           |
    +-----------------------+-----------+-----------+
