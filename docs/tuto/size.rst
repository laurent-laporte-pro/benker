.. _benker__size:

Size
====

Description
-----------

A :class:`~benker.size.Size` is a tuple with *width*, *height* coordinates.
It represents the width and the height of a cell in a grid.

.. doctest:: size

    >>> from benker.size import Size

    >>> size = Size(4, 5)

The representation of a size is "(*width* x *height*)":

.. doctest:: size

    >>> print(size)
    (4 x 5)


Operations
----------

You can change the size of a *Size* by adding, subtracting of multiplying values.

You can add two sizes, a size and a tuple (*x*, *y*), a size and a single quantity (integer):

.. doctest:: size

    >>> Size(2, 3) + Size(3, 4)
    Size(width=5, height=7)

    >>> Size(2, 3) + (3, 4)
    Size(width=5, height=7)

    >>> Size(2, 3) + 1
    Size(width=3, height=4)

You can subtract two sizes, a size and a tuple (*x*, *y*), a size and a single quantity (integer):

.. doctest:: size

    >>> Size(1, 4) - Size(2, 1)
    Size(width=-1, height=3)

    >>> Size(1, 4) - (2, 1)
    Size(width=-1, height=3)

    >>> Size(1, 4) - 1
    Size(width=0, height=3)

You can multiply a size by an integer.
This last ability is useful to reverse a size:

.. doctest:: size

    >>> Size(3, 4) * 3
    Size(width=9, height=12)

    >>> Size(3, 4) * -1
    Size(width=-3, height=-4)

You can also negate a size:

.. doctest:: size

    >>> -Size(3, 5)
    Size(width=-3, height=-5)

    >>> +Size(3, 5)
    Size(width=3, height=5)

All this operations are useful to do mathematical transformation
with :ref:`Coord — Operations <benker__coord__operations>`, for instance,
a translation of a coord is done by adding a coord and a size.
