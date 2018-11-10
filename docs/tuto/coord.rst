.. _benker__coord:

Coord
=====

Description
-----------

A :class:`~benker.coord.Coord` is a tuple with *x*, *y* coordinates.
It represents the top-left origin of a cell in a grid.

.. doctest:: coord

    >>> from benker.coord import Coord

    >>> coord = Coord(4, 5)

The origin of the grid is the coord (1, 1).

.. doctest:: coord

    >>> from benker.coord import PT_ORIGIN

    >>> PT_ORIGIN
    Coord(x=1, y=1)

We use the Excel convention to represent a *Coord*:
columns are represented by letters,
rows are represented by numbers.

.. doctest:: coord

    >>> print(Coord(2, 5))
    B5

.. _benker__coord__operations:

Operations
----------

Mathematical operations are an easy way to translate a *Coord* to another locations.

You can use a :ref:`benker__size` to move a coord to another position.
You can also use a tuple (*x*, *y*) or a single quantity (integer):

.. doctest:: coord

    >>> from benker.size import Size

    >>> Coord(2, 5) + Size(1, 2)
    Coord(x=3, y=7)

    >>> Coord(2, 5) + (1, 2)
    Coord(x=3, y=7)

    >>> Coord(2, 5) + 1
    Coord(x=3, y=6)

The translation can be positive or negative:

.. doctest:: coord

    >>> Coord(2, 5) - Size(1, 2)
    Coord(x=1, y=3)

    >>> Coord(2, 5) - (1, 2)
    Coord(x=1, y=3)

    >>> Coord(2, 5) - 1
    Coord(x=1, y=4)

You cannot add or subtract two coordinates:

.. doctest:: coord

    >>> Coord(2, 5) + Coord(2, 1)
    Traceback (most recent call last):
        ...
    TypeError: <class 'benker.coord.Coord'>

    >>> Coord(2, 5) - Coord(1, 2)
    Traceback (most recent call last):
        ...
    TypeError: <class 'benker.coord.Coord'>

Again, you cannot add a size and a coord:

.. doctest:: coord

    >>> Size(2, 5) + Coord(2, 1)
    Traceback (most recent call last):
        ...
    TypeError: <class 'benker.coord.Coord'>

    >>> Size(2, 5) - Coord(1, 2)
    Traceback (most recent call last):
        ...
    TypeError: <class 'benker.coord.Coord'>

.. important::

    This constraint must be respected in order to help diagnosing conceptual errors.
