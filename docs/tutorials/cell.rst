.. _benker__cell:

Cell
====

Description
-----------

A :class:`~benker.cell.Cell` object stores the *content* of a :class:`~benker.grid.Grid` cell.

A cell can have *styles*, a dictionary of key-value properties attached to the cell.

A cell has a *type* to distinguish between header, body and footer cells.
The default type is "body", but you can also use "header", "footer" or whatever…

A cell has top-left coordinates: *x* and *y*. The default coordinates is (1, 1):
this is the top-left coordinate of the cell box.
The coordinates *x* and *y* cannot be null: grid coordinates are 1-indexed.

A cell has a size: *width* and *height*. The default size is (1, 1), you can
increase them to represent horizontal or vertical spanning.
The *width* and the *height* cannot be null.

To instantiate a :class:`~benker.cell.Cell`, you can do:

.. doctest:: cell

    >>> from benker.cell import Cell

    >>> c1 = Cell("c1")
    >>> c2 = Cell("c2", styles={'color': 'red'})
    >>> c3 = Cell("c3", x=2, y=3, type="footer")
    >>> c4 = Cell("c4", width=2)
    >>> c5 = Cell("c5", height=2)

The string representation of a cell is the string representation of it's content:

.. doctest:: cell

    >>> for cell in c1, c2, c3, c4, c5:
    ...     print(cell)
    c1
    c2
    c3
    c4
    c5


Attributes
----------

A cell has the following attributes:

-   *content* is the user-defined cell content. It can be of any type: ``None``,
    :class:`str`, :class:`int`, :class:`float`, a container (:class:`list`),
    a XML element, etc. The same content can be shared by several cells, it's
    your own responsibility to handle the copy (or deep copy) of the *content*
    reference when needed.

    .. note::

        In a :class:`~benker.grid.Grid`, the :ref:`merging <benker__grid__merging>`
        of two cell contents is done with the "+" operator (:func:`~operator.__add__`).
        You can override this by using a *content_appender*, a two-arguments
        function which will perform the concatenation of the two contents.

-   *styles* is the user-defined cell styles: a dictionary of key-value pairs.
    This values are useful to store some HTML-like styles (border-style,
    border-width, border-color, vertical-align, text-align, etc.).
    Of course, we are not tied to the HTML-like styles, you can use your own
    styles list.

    .. note::

        The style dictionary is always copied: in other words, key-value pairs
        are copied but a shallow copy is done for the values (in general, it
        is not a problem if you use non-mutable values like :class:`str`).

-   *type* is a way to distinguish the body cells, from the header and the footer.
    The default value is "body", but you can use "header", "footer" or whatever
    is suitable for your needs.

    .. note::

        In a :class:`~benker.grid.Grid`, the :ref:`merging <benker__grid__merging>`
        of two cell types is done by keeping the first cell type and
        dropping the second one. In other words, the resulting cell type is
        the type of the most top-left cell type of the merged cells.

Using the cell attributes:

.. doctest:: cell

    >>> paragraphs = ["Hello", "How are you?"]
    >>> css = {'text-align': 'justify', 'vertical-align': 'top'}

    >>> c1 = Cell(paragraphs, styles=css, type="normal")
    >>> c2 = Cell(paragraphs, styles=css, type="normal")

    # this will mutate the referenced *paragraphs* list:
    >>> c1.content.append("I am well.")
    >>> c2.content
    ['Hello', 'How are you?', 'I am well.']

    # this will change only the cell styles:
    >>> c1.styles['vertical-align'] = 'middle'
    >>> c2.styles
    {'text-align': 'justify', 'vertical-align': 'top'}


Properties
----------

You can use the following properties to extract information from a *cell*:

- use *min* to get the top-left corner coordinates,
- use *max* to get the bottom-right corner coordinates,
- use *width* to get the width of the box (number of columns),
- use *height* to get the height of the box (number of rows),
- use *size* to get the size (*width* and *height*) of the box.

.. doctest:: cell

    >>> c1 = Cell("Hi", x=5, y=6, width=3, height=2)

    >>> c1.min
    Coord(x=5, y=6)
    >>> c1.max
    Coord(x=7, y=7)
    >>> c1.width
    3
    >>> c1.height
    2
    >>> c1.size
    Size(width=3, height=2)

.. important::

    All properties are non-mutable:

    .. doctest:: cell

        >>> c1.width = 9
        Traceback (most recent call last):
        ...
        AttributeError: can't set attribute


.. _benker__cell__operations:

Operations
----------

.. _benker__cell__contains:

Contains
~~~~~~~~

You can check if a point, defined by its coordinates (tuple (*x*, *y*) or
:class:`~benker.coord.Coord` instance), is contained in a
:class:`~benker.cell.Cell`.

A cell contains a point if it is in its :class:`~benker.box.Box`.
This rule is explained in detail in the section :ref:`Box – Contains <benker__box__contains>`.

.. doctest:: cell

    >>> c1 = Cell("A", x=2, y=3, width=2, height=1)

    >>> (3, 3) in c1
    True
    >>> (7, 9) in c1
    False


.. _benker__cell__total_ordering:

Total ordering
--------------

A total ordering is defined for the cells.
The aim is to order the cells in a grid sorted from left to right and from top to bottom.
This order is useful to group the cells by rows.

The total ordering is base on the :class:`~benker.box.Box` :ref:`benker__box__total_ordering`.

.. doctest:: cell

    >>> c1 = Cell("one")
    >>> c2 = Cell("two", x=2)
    >>> c3 = Cell("three", y=2)

    >>> c1 < c2 < c3
    True

This total ordering allow us to sort the cells:

.. doctest:: cell

    >>> from random import shuffle

    >>> cells = [c1, c2, c3]
    >>> shuffle(cells)
    >>> [str(cell) for cell in sorted(cells)]
    ['one', 'two', 'three']


.. _benker__cell__transformations:

Transformations
~~~~~~~~~~~~~~~

It is possible to change the cell position and size by using two kind of transformations:

-   Move a cell to a different coordinates,
-   Resize a cell.

.. doctest:: cell

    >>> from benker.coord import Coord
    >>> from benker.size import Size

    >>> c1 = Cell("A")
    >>> c1
    <Cell('A', styles={}, type='body', x=1, y=1, width=1, height=1)>

    >>> c1.move_to(Coord(2, 3))
    <Cell('A', styles={}, type='body', x=2, y=3, width=1, height=1)>

    >>> c1.resize(Size(3, 4))
    <Cell('A', styles={}, type='body', x=1, y=1, width=3, height=4)>

    >>> c1.transform(Coord(2, 3), Size(3, 4))
    <Cell('A', styles={}, type='body', x=2, y=3, width=3, height=4)>

The transformation functions don't change the current cell but produce
a new one with new coordinates/size.
