.. _benker__box:

Box
===

Description
-----------

A :class:`~benker.box.Box` is a rectangular area defined by two coordinates:

- the top-left corner of the rectangle: the *min* coord,
- the bottom-right corner of the rectangle: the *max* coord.

The default size of a *Box* is (1, 1),
so you can create a *box* by only specifying the top-let corner of the rectangle.

.. doctest:: box

    >>> from benker.box import Box

    >>> Box(1, 2, 2, 3)
    Box(min=Coord(x=1, y=2), max=Coord(x=2, y=3))
    >>> Box(1, 2)
    Box(min=Coord(x=1, y=2), max=Coord(x=1, y=2))

You can use two coordinates to define a box:

.. doctest:: box

    >>> from benker.coord import Coord

    >>> Box(Coord(5, 6), Coord(7, 8))
    Box(min=Coord(x=5, y=6), max=Coord(x=7, y=8))
    >>> Box(Coord(5, 6))
    Box(min=Coord(x=5, y=6), max=Coord(x=5, y=6))

You can specify the size of a box:

.. doctest:: box

    >>> from benker.size import Size

    >>> Box(Coord(5, 6), Size(3, 2))
    Box(min=Coord(x=5, y=6), max=Coord(x=7, y=7))

We use the Excel convention to represent a *Box*:
columns are represented by letters,
rows are represented by numbers.

.. doctest:: box

    >>> print(Box(Coord(2, 5)))
    B5
    >>> print(Box(Coord(2, 5), Size(3, 2)))
    B5:D6

.. _benker__box__properties:


Properties
----------

You can use the following properties to extract information from a *box*:

- use *min* to get the top-left corner coordinates,
- use *max* to get the bottom-right corner coordinates,
- use *width* to get the width of the box (number of columns),
- use *height* to get the height of the box (number of rows),
- use *size* to get the size (*width* and *height*) of the box.

.. doctest:: box

    >>> b1 = Box(Coord(5, 6), Size(3, 2))

    >>> b1.min
    Coord(x=5, y=6)
    >>> b1.max
    Coord(x=7, y=7)
    >>> b1.width
    3
    >>> b1.height
    2
    >>> b1.size
    Size(width=3, height=2)

.. important::

    All properties are non-mutable:

    .. doctest:: box

        >>> b1.width = 9
        Traceback (most recent call last):
        ...
        AttributeError: can't set attribute


Operations
----------

Contains
~~~~~~~~

You can check if a point, defined by its coordinates (tuple (*x*, *y*) or
:class:`~benker.coord.Coord` instance), is contained in a box:

.. doctest:: box

    >>> top_left = Coord(5, 6)
    >>> top_right = Coord(6, 6)
    >>> bottom_left = Coord(5, 8)
    >>> bottom_right = Coord(6, 8)

    >>> b1 = Box(top_left, bottom_right)

    >>> top_left in b1
    True
    >>> top_right in b1
    True
    >>> bottom_left in b1
    True
    >>> bottom_right in b1
    True

    >>> Coord(7, 6) in b1
    False

    >>> (5, 7) in b1
    True

.. important::

    Even if a :class:`~benker.size.Size` object is a subtype of :class:`tuple`,
    such an object cannot be "contained" in a :class:`~benker.box.Box`.

    .. doctest:: box

        >>> b1 = Box(Coord(x=5, y=6), Coord(x=6, y=8))
        >>> Size(5, 7) in b1
        Traceback (most recent call last):
            ...
        TypeError: <class 'benker.size.Size'>

You can check if a :class:`~benker.box.Box` is contained in another box:

.. doctest:: box

    >>> b1 = Box(Coord(x=5, y=6), Coord(x=6, y=8))
    >>> b2 = Box(Coord(x=5, y=7), Coord(x=6, y=7))
    >>> b3 = Box(Coord(x=6, y=6), Coord(x=7, y=6))

    >>> b1 in b1
    True
    >>> b2 in b1
    True
    >>> b3 in b2
    False


Intersection and Union
~~~~~~~~~~~~~~~~~~~~~~

You can find if a *Box* intersects another *Box*:

.. doctest:: box

    >>> b1 = Box(Coord(x=1, y=1), Coord(x=3, y=3))
    >>> b2 = Box(Coord(x=2, y=2), Coord(x=4, y=4))
    >>> b3 = Box(Coord(x=4, y=1), Coord(x=5, y=1))

    >>> b1.intersect(b2)
    True
    >>> b1.intersect(b3)
    False

Two boxes are disjoint if they don't intersect each other:

.. doctest:: box

    >>> b1.isdisjoint(b2)
    False
    >>> b1.isdisjoint(b3)
    True

You can calculate the intersection of two boxes.
You can use the "&" operator to do that:

.. doctest:: box

    >>> b1.intersection(b2)
    Box(min=Coord(x=2, y=2), max=Coord(x=3, y=3))
    >>> b1 & b2
    Box(min=Coord(x=2, y=2), max=Coord(x=3, y=3))

.. important::

    If the two boxes are disjoint, there is no intersection:

    .. doctest:: box

        >>> b1 & b3
        Traceback (most recent call last):
          ...
        ValueError: (Box(min=Coord(x=1, y=1), max=Coord(x=3, y=3)), Box(min=Coord(x=4, y=1), max=Coord(x=5, y=1)))

You can calculate the union of two boxes.
The union of two boxes is the bounding box:
You can use the "|" operator to do that:

.. doctest:: box

    >>> b1.union(b2)
    Box(min=Coord(x=1, y=1), max=Coord(x=4, y=4))
    >>> b1 | b2
    Box(min=Coord(x=1, y=1), max=Coord(x=4, y=4))


Total ordering
--------------

A total ordering is defined for the boxes.
The aim is to order the cells in a grid sorted from left to right and from top to bottom.
This order is useful to group the cells by rows.

You can compare boxes:

.. doctest:: box

    >>> b1 = Box(Coord(3, 2), Coord(6, 4))
    >>> b1 < b1
    False
    >>> b1 < Box(Coord(3, 2), Coord(6, 5))
    True
    >>> b1 < Box(Coord(3, 2), Coord(7, 4))
    True
    >>> b1 < Box(Coord(4, 2), Coord(6, 4))
    True
    >>> b1 < Box(Coord(3, 3), Coord(6, 4))
    True

You can sort boxes. The sort order can be defined as below:

- top cells are sorted before bottom cells,
- top-left cells are sorted before top-right cells,
- smaller cells are sorted before bigger.

.. doctest:: box

    >>> from random import shuffle

    >>> boxes = [Box(x, y) for x in range(1, 4) for y in range(1, 3)]
    >>> [str(box) for box in boxes]
    ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']

    >>> shuffle(boxes)
    >>> [str(box) for box in sorted(boxes)]
    ['A1', 'B1', 'C1', 'A2', 'B2', 'C2']
