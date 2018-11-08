.. _benker__point:

Point
=====

Description
-----------

A *Point* is a tuple with *x*, *y* coordinates.
It represents the top-left origin of a cell in a grid.

.. doctest:: point

    >>> from benker.point import Point

    >>> pt = Point(4, 5)

The origin of the grid is the point (1, 1).

.. doctest:: point

    >>> from benker.point import PT_ORIGIN

    >>> PT_ORIGIN
    Point(x=1, y=1)

We use the Excel convention to represent a *Point*:
columns are represented by letters,
rows are represented by numbers.

.. doctest:: point

    >>> print(Point(2, 5))
    B5

.. _benker__point__operations:

Operations
----------

Mathematical operations are an easy way to translate a *Point* to another locations.

You can use a :ref:`benker__dimension` to move a point to another position.
You can also use a tuple (*x*, *y*) or a single quantity (integer):

.. doctest:: point

    >>> from benker.dimension import Dimension

    >>> Point(2, 5) + Dimension(1, 2)
    Point(x=3, y=7)

    >>> Point(2, 5) + (1, 2)
    Point(x=3, y=7)

    >>> Point(2, 5) + 1
    Point(x=3, y=6)

The translation can be positive or negative:

.. doctest:: point

    >>> Point(2, 5) - Dimension(1, 2)
    Point(x=1, y=3)

    >>> Point(2, 5) - (1, 2)
    Point(x=1, y=3)

    >>> Point(2, 5) - 1
    Point(x=1, y=4)

You cannot add or subtract two points:

.. doctest:: point

    >>> Point(2, 5) + Point(2, 1)
    Traceback (most recent call last):
        ...
    TypeError: <class 'benker.point.Point'>

    >>> Point(2, 5) - Point(1, 2)
    Traceback (most recent call last):
        ...
    TypeError: <class 'benker.point.Point'>

Again, you cannot add a dimension and a point:

.. doctest:: point

    >>> Dimension(2, 5) + Point(2, 1)
    Traceback (most recent call last):
        ...
    TypeError: <class 'benker.point.Point'>

    >>> Dimension(2, 5) - Point(1, 2)
    Traceback (most recent call last):
        ...
    TypeError: <class 'benker.point.Point'>

.. important::

    This constraint must be respected in order to help diagnosing conceptual errors.
