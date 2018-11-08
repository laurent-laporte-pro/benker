.. _benker__point:

.. doctest:: point
    :hide:

    >>> from benker.point import Point
    >>> from benker.point import Dimension
    >>> from benker.point import PT_ORIGIN


Playing with Point and Dimension
================================

Point
-----

A *Point* is a tuple with *x*, *y* coordinates.
It represents the top-left origin of a cell in a grid.

.. doctest:: point

    >>> pt = Point(4, 5)

The origin of the grid is the point (1, 1).

.. doctest:: point

    >>> PT_ORIGIN
    Point(x=1, y=1)

We use the Excel convention to represent a *Point*:
columns are represented by letters,
rows are represented by numbers.

    >>> print(Point(2, 5))
    B5


Dimension
---------

A *Dimension* is a tuple with *width*, *height* coordinates.
It represents the width and the height of a cell in a grid.

.. doctest:: point

    >>> dim = Dimension(4, 5)

The representation of a dimension is "(*width* x *height*):

    >>> print(dim)
    (4 x 5)
