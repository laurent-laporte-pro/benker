.. _benker__dimension:

Dimension
=========

Description
-----------

A *Dimension* is a tuple with *width*, *height* coordinates.
It represents the width and the height of a cell in a grid.

.. doctest:: dimension

    >>> from benker.dimension import Dimension

    >>> dim = Dimension(4, 5)

The representation of a dimension is "(*width* x *height*):

.. doctest:: dimension

    >>> print(dim)
    (4 x 5)


Operations
----------

You can change the size of a *Dimension* by adding, subtracting of multiplying values.

You can add two dimensions, a dimension and a tuple (*x*, *y*), a dimension and a single quantity (integer):

.. doctest:: dimension

    >>> Dimension(2, 3) + Dimension(3, 4)
    Dimension(width=5, height=7)

    >>> Dimension(2, 3) + (3, 4)
    Dimension(width=5, height=7)

    >>> Dimension(2, 3) + 1
    Dimension(width=3, height=4)

You can subtract two dimensions, a dimension and a tuple (*x*, *y*), a dimension and a single quantity (integer):

.. doctest:: dimension

    >>> Dimension(1, 4) - Dimension(2, 1)
    Dimension(width=-1, height=3)

    >>> Dimension(1, 4) - (2, 1)
    Dimension(width=-1, height=3)

    >>> Dimension(1, 4) - 1
    Dimension(width=0, height=3)

You can multiply a dimension by an integer.
This last ability is useful to reverse a dimension:

.. doctest:: dimension

    >>> Dimension(3, 4) * 3
    Dimension(width=9, height=12)

    >>> Dimension(3, 4) * -1
    Dimension(width=-3, height=-4)

You can also negate a dimension:

.. doctest:: dimension

    >>> -Dimension(3, 5)
    Dimension(width=-3, height=-5)

    >>> +Dimension(3, 5)
    Dimension(width=3, height=5)

All this operations are useful to do mathematical transformation
with :ref:`Point — Operations <benker__point__operations>`, for instance,
a translation of a point is done by adding a point and a dimension.
