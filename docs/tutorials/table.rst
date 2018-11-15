.. _benker__table:

Table
=====

.. _benker__table__description:

Description
-----------

A :class:`~benker.table.Table` is a data structure used to represent
Office Open XML tables, CALS tables or HTML tables.

A :class:`~benker.table.Table` is a :class:`~benker.styled.Styled` object,
so you can attach a dictionary of styles and a cell group ("body" by default).
The cell group is used to give a default value to the the row/column views.

.. doctest:: table

    >>> from benker.table import Table

    >>> Table(styles={'frame': 'all'})
    <Table({'frame': 'all'}, 'body')>

A table can be initialize with a collection of cells.
Make sure all cells are disjoints.

.. doctest:: table

    >>> from benker.cell import Cell

    >>> red = Cell('red', x=1, y=1, height=2)
    >>> pink = Cell('pink', x=2, y=1, width=2)
    >>> blue = Cell('blue', x=2, y=2)

    >>> Table([red, pink, blue])
    <Table({}, 'body')>

.. important::

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
    >>> row.cell_group = "header"
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
