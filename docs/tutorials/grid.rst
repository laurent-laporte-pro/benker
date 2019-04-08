.. _benker__grid:

Grid
====

Description
-----------

A :class:`~benker.grid.Grid` is a collection of :class:`~benker.cell.Cell`
objects ordered in a grid of rows and columns.

You can define a empty grid like this:

.. doctest:: grid

    >>> from benker.grid import Grid

    >>> Grid()
    Grid([])

You can also define a grid from a collection (:class:`~list`, :class:`~set`…) of cells.
Cells are ordered according to the total ordering of the cell boxes:

.. doctest:: grid

    >>> from benker.cell import Cell

    >>> red = Cell('red', x=1, y=1, height=2)
    >>> pink = Cell('pink', x=2, y=1, width=2)
    >>> blue = Cell('blue', x=2, y=2)

    >>> grid = Grid([red, blue, pink])
    >>> for cell in grid:
    ...     print(cell)
    red
    pink
    blue

.. warning::

    If at least one cell intersect another one, an exception is raised:

    .. doctest:: grid

        >>> Grid([Cell("one"), Cell("two")])
        Traceback (most recent call last):
            ...
        KeyError: Coord(x=1, y=1)

    So, it is important to define the coordinates of the cells.

It's easy to copy the cells of another grid.

Remember that:

- cells are copied (not shared between grids),
- cell contents are shared: two different cells share the same content,
- cell styles are copied (but not deeply).

.. doctest:: grid

    >>> grid1 = Grid([red, blue, pink])
    >>> grid2 = Grid(grid1)

    >>> tuple(id(cell) for cell in grid1) != tuple(id(cell) for cell in grid2)
    True
    >>> tuple(id(cell.content) for cell in grid1) == tuple(id(cell.content) for cell in grid2)
    True
    >>> tuple(id(cell.styles) for cell in grid1) != tuple(id(cell.styles) for cell in grid2)
    True

You can pretty print a grid:

.. doctest:: grid

    >>> grid = Grid([red, blue, pink])
    >>> print(grid)
    +-----------+-----------------------+
    |    red    |   pink                |
    |           +-----------+-----------+
    |           |   blue    |           |
    +-----------+-----------+-----------+


.. _benker__grid__properties:

Properties
----------

The bounding box of a grid is the bounding box of all cells:

.. doctest:: grid

    >>> grid = Grid()
    >>> grid[1, 1] = Cell("red", height=2)
    >>> grid[2, 1] = Cell("pink", width=2)
    >>> grid[3, 2] = Cell("gray")
    >>> print(grid)
    +-----------+-----------------------+
    |    red    |   pink                |
    |           +-----------+-----------+
    |           |           |   gray    |
    +-----------+-----------+-----------+

    >>> grid.bounding_box
    Box(min=Coord(x=1, y=1), max=Coord(x=3, y=2))

.. important::

    The bounding box is not defined for an empty grid, so ``None`` is returned
    in that case (this behavior is preferable to raising an exception,
    in order to simplify interactive debugging).

    .. doctest:: grid

        >>> grid = Grid()
        >>> grid.bounding_box is None
        True


.. _benker__grid__operations:

Operations
----------

.. _benker__grid__contains:

Contains
~~~~~~~~

You can check if a point, defined by its coordinates (tuple (*x*, *y*) or
:class:`~benker.coord.Coord` instance), is contained in a
:class:`~benker.grid.Grid`.

The rule is simple: a grid contains a point if it exists a
:class:`~benker.cell.Cell` of the grid which contains that point. In other
words, a point may be contained in the bounding box of a grid but not in any
cell if there are some gaps in the grid.

.. doctest:: grid

    >>> from benker.coord import Coord

    >>> red = Cell('red', x=1, y=1, height=2)
    >>> pink = Cell('pink', x=2, y=1, width=2)
    >>> blue = Cell('blue', x=2, y=2)
    >>> grid = Grid([red, blue, pink])

    >>> (1, 1) in grid
    True
    >>> (3, 1) in grid
    True
    >>> (4, 1) in grid
    False
    >>> (3, 2) in grid
    False

    >>> Coord(1, 2) in grid
    True


Set, Get, Delete cells
~~~~~~~~~~~~~~~~~~~~~~

A grid is a :class:`~collections.abc.MutableMapping`, it works like a dictionary
of cells. Keys of the dictionary are coordinates (tuple (*x*, *y*)
or :class:`~benker.coord.Coord` instance).
The coordinates are the top-left coordinates of the cells.

.. doctest:: grid

    >>> grid = Grid()
    >>> grid[1, 1] = Cell("red", height=2)
    >>> grid[2, 1] = Cell("pink", width=2)
    >>> grid[2, 2] = Cell("blue")
    >>> grid[3, 2] = Cell("gray")

    >>> print(grid)
    +-----------+-----------------------+
    |    red    |   pink                |
    |           +-----------+-----------+
    |           |   blue    |   gray    |
    +-----------+-----------+-----------+

.. warning::

    Unlike a :class:`~dict`, you cannot set a cell to a given location
    if a cell already exist in that location, an exception is raised in that case.

    .. doctest:: grid

        >>> grid[3, 1] = Cell("purple")
        Traceback (most recent call last):
            ...
        KeyError: Coord(x=3, y=1)

You can get a cell at a given location:

.. doctest:: grid

    >>> grid[1, 1]
    <Cell('red', styles={}, nature='body', x=1, y=1, width=1, height=2)>
    >>> grid[3, 1]
    <Cell('pink', styles={}, nature='body', x=2, y=1, width=2, height=1)>

You can delete a cell at a given location:

.. doctest:: grid

    >>> del grid[3, 1]
    >>> print(grid)
    +-----------+-----------+-----------+
    |    red    |           |           |
    |           +-----------+-----------+
    |           |   blue    |   gray    |
    +-----------+-----------+-----------+


.. _benker__grid__merging:

Merging/expanding
~~~~~~~~~~~~~~~~~

It is possible to merge several cells in the grid.
The merging takes the *start* coordinates and the *end* coordinates
of the cells to merge.

We can define a *content_appender* to give the content merging operation
to use to merge several cell contents.

.. doctest:: grid

    >>> grid = Grid()
    >>> grid[1, 1] = Cell("red", height=2)
    >>> grid[2, 1] = Cell("pink")
    >>> grid[3, 1] = Cell("blue")
    >>> print(grid)
    +-----------+-----------+-----------+
    |    red    |   pink    |   blue    |
    |           +-----------+-----------+
    |           |           |           |
    +-----------+-----------+-----------+

    >>> grid.merge((2, 1), (3, 1), content_appender=lambda a, b: "/".join([a, b]))
    <Cell('pink/blue', styles={}, nature='body', x=2, y=1, width=2, height=1)>
    >>> print(grid)
    +-----------+-----------------------+
    |    red    | pink/blue             |
    |           +-----------+-----------+
    |           |           |           |
    +-----------+-----------+-----------+

.. warning::

    All cells in the bounding box of the merging must be inside of the bounding box.
    In other words, the bounding box of the merging must not intersect any cell
    in the grid.

    .. doctest:: grid

        >>> grid.merge((1, 2), (2, 2))
        Traceback (most recent call last):
          ...
        ValueError: ((1, 2), (2, 2))

Similar to the merging, you can expand the size of a cell;

.. doctest:: grid

    >>> grid = Grid()
    >>> grid[1, 1] = Cell("red", height=2)
    >>> grid[2, 1] = Cell("pink")
    >>> grid[3, 1] = Cell("blue")
    >>> print(grid)
    +-----------+-----------+-----------+
    |    red    |   pink    |   blue    |
    |           +-----------+-----------+
    |           |           |           |
    +-----------+-----------+-----------+

    >>> grid.expand((2, 1), height=1)
    <Cell('pink', styles={}, nature='body', x=2, y=1, width=1, height=2)>
    >>> print(grid)
    +-----------+-----------+-----------+
    |    red    |   pink    |   blue    |
    |           |           +-----------+
    |           |           |           |
    +-----------+-----------+-----------+


.. _benker__grid__iterators:

Iterators
~~~~~~~~~

You can iterate the cells of a grid:

.. doctest:: grid

    >>> grid = Grid()
    >>> grid[1, 1] = Cell("red", height=2)
    >>> grid[2, 1] = Cell("hot", width=2)
    >>> grid[2, 2] = Cell("chili")
    >>> grid[3, 2] = Cell("peppers")
    >>> grid[1, 3] = Cell("Californication", width=3)

    >>> print(grid)
    +-----------+-----------------------+
    |    red    |    hot                |
    |           +-----------+-----------+
    |           |   chili   |  peppers  |
    +-----------------------------------+
    |             Californi             |
    +-----------------------------------+

    >>> for cell in grid:
    ...     print(cell)
    red
    hot
    chili
    peppers
    Californication

You can iterate over the grid rows with the method
:meth:`~benker.grid.Grid.iter_rows`. Each row is a :class:`tuple` of cells:

.. doctest:: grid

    >>> for row in grid.iter_rows():
    ...     print(" / ".join(cell.content for cell in row))
    red / hot
    chili / peppers
    Californication
