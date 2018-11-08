# coding: utf-8
u"""
Box
===

A *Box* is a rectangular area defined by two *Points*:

- the top-left corner of the rectangle: the *min* point,
- the bottom-right corner of the rectangle: the *max* point.

.. doctest:: box_demo
    :hide:

    >>> from benker.box import Box
    >>> from benker.point import Point

To instantiate a :class:`~benker.box.Box`, you can do:

.. doctest:: box_demo

    >>> b1 = Box(Point(5, 6), Point(7, 8))
    >>> b2 = Box(Point(5, 6))
    >>> b3 = Box(1, 2, 2, 3)
    >>> b4 = Box(1, 2)
    >>> b5 = Box(b1)

*Box* objects have a string representation à la Excel:

.. doctest:: box_demo

    >>> for box in b1, b2, b3, b4, b5:
    ...     print(box)
    E6:G8
    E6
    A2:B3
    A2
    E6:G8

You can calculate the *width* and *eight* of boxes:

.. doctest:: box_demo

    >>> b1 = Box(Point(5, 6), Point(6, 8))
    >>> b1.width, b1.height
    (2, 3)

    >>> b2 = Box(Point(5, 6))
    >>> b2.width, b2.height
    (1, 1)

You determine if a *Point* or a *Box* is included in a *Box*:

.. doctest:: box_demo

    >>> top_left = Point(5, 6)
    >>> top_right = Point(6, 6)
    >>> bottom_left = Point(5, 8)
    >>> bottom_right = Point(6, 8)

    >>> b1 = Box(top_left, bottom_right)

    >>> top_left in b1
    True
    >>> top_right in b1
    True
    >>> bottom_left in b1
    True
    >>> bottom_right in b1
    True

    >>> Point(7, 6) in b1
    False

    >>> (5, 7) in b1
    True

You determine two boxes intersect each other, or are disjoints:

.. doctest:: box_demo

    >>> b1 = Box(Point(5, 6), Point(6, 8))
    >>> b2 = Box(Point(6, 6), Point(6, 7))
    >>> b3 = Box(Point(7, 6), Point(7, 8))
    >>> b2.intersect(b3)
    False
    >>> b1.isdisjoint(b2)
    False
    >>> b2.isdisjoint(b1)
    False
    >>> b1.isdisjoint(b3)
    True
    >>> b3.isdisjoint(b1)
    True

"""
import collections
import functools

from benker.dimension import Dimension
from benker.point import Point


@functools.total_ordering
class Box(collections.namedtuple('Box', ['min', 'max'])):
    """
    A *Box* is a rectangular area defined by a *min* and
    a *max* :class:`~benker.point.Point`.

    Usage:

    >>> from benker.box import Box

    >>> box = Box(1, 1, 5, 3)
    >>> box
    Box(min=Point(x=1, y=1), max=Point(x=5, y=3))

    :ivar Point min: top-left corner of the rectangle.
    :ivar Point max: bottom-right corner of the rectangle.
    """
    __slots__ = ()

    def __new__(cls, *args):
        """
        Construct a new *Box*.

        :param args:
            Arguments could be:

            - top-left and bottom-right points of the box: Point(*min_pt*, *max_pt*);
            - top-left coordinates and box dimensions: Point(*min_pt*, *max_pt*), Dimension(*width*, *height*);
            - top-left point of the box: Point(*min_pt*, *max_pt*),
              assuming box width is (1, 1),
            - coordinates of the box: *min_x*, *min_y*, *max_x*, *max_y*;
            - coordinates of the top-left point: *min_x*, *min_y*,
              assuming box width is (1, 1);
            - another box.

        :return: The new *Box*.

        :raises TypeError:
            if the arguments are of incompatible types.

        :raises ValueError:
        """
        types = tuple(map(type, args))
        if types == (Point, Point):
            min_x, min_y = args[0]
            max_x, max_y = args[1]
        elif types == (Point, Dimension):
            min_x, min_y = args[0]
            max_x, max_y = args[0] + args[1] - 1
        elif types == (Point,):
            min_x, min_y = args[0]
            max_x, max_y = min_x, min_y
        elif types == (int, int, int, int):
            min_x, min_y, max_x, max_y = args
        elif types == (int, int):
            min_x, min_y = args
            max_x, max_y = min_x, min_y
        elif types == (cls,):
            # no duplicate
            return args[0]
        else:
            raise TypeError(repr(types))
        if 0 < min_x <= max_x and 0 < min_y <= max_y:
            min_pt = Point(min_x, min_y)
            max_pt = Point(max_x, max_y)
            # noinspection PyArgumentList
            return super(Box, cls).__new__(cls, min_pt, max_pt)
        raise ValueError(*args)

    def __str__(self):
        if (self.width, self.height) == (1, 1):
            return str(self.min)
        return str(self.min) + ':' + str(self.max)

    @property
    def width(self):
        # type: () -> int
        return self.max.x - self.min.x + 1

    @property
    def height(self):
        # type: () -> int
        return self.max.y - self.min.y + 1

    @property
    def dim(self):
        return Dimension(self.width, self.height)

    def transform(self, target=None, dim=None):
        min_pt = target or self.min
        dim = dim or self.dim
        max_pt = min_pt + dim - 1
        return Box(min_pt, max_pt)

    def move_to(self, target):
        return self.transform(target=target)

    def resize(self, dim):
        return self.transform(dim=dim)

    def __contains__(self, other):
        if isinstance(other, tuple) and tuple(map(type, other)) == (int, int):
            return self.min.x <= other[0] <= self.max.x and self.min.y <= other[1] <= self.max.y
        elif isinstance(other, Point):
            # The ``None`` value means "anywhere"
            if other.x is None and other.y is None:
                return True
            elif other.x is None:
                return self.min.y <= other.y <= self.max.y
            elif other.y is None:
                return self.min.x <= other.x <= self.max.x
            else:
                return self.min.x <= other.x <= self.max.x and self.min.y <= other.y <= self.max.y
        elif isinstance(other, Box):
            return ((self.min.x <= other.min.x <= self.max.x and self.min.y <= other.min.y <= self.max.y) and
                    (self.min.x <= other.max.x <= self.max.x and self.min.y <= other.max.y <= self.max.y))
        else:
            raise TypeError(repr(type(other)))

    def intersect(self, that):
        # type: (Box) -> bool
        return ((self.min in that or self.max in that) or
                (that.min in self or that.max in self))

    def isdisjoint(self, that):
        # type: (Box) -> bool
        return not self.intersect(that)

    def union(self, *others):
        """
        Return the union of *self* and all the *boxes*.

        Usage:

        >>> from benker.box import Box
        >>> from benker.point import Point

        >>> b1 = Box(Point(3, 2), Point(6, 4))
        >>> b2 = Box(Point(4, 3), Point(5, 7))
        >>> b1.union(b2)
        Box(min=Point(x=3, y=2), max=Point(x=6, y=7))

        >>> b1 | b2
        Box(min=Point(x=3, y=2), max=Point(x=6, y=7))

        :param others: collections of boxes

        :return: The bounding box of all the boxes.
        """
        boxes = (self,) + others
        min_list = tuple(box.min for box in boxes)
        min_pt = Point(min(pt.x for pt in min_list), min(pt.y for pt in min_list))
        max_list = tuple(box.max for box in boxes)
        max_pt = Point(max(pt.x for pt in max_list), max(pt.y for pt in max_list))
        bounding_box = Box(min_pt, max_pt)
        assert all(box in bounding_box for box in boxes)
        return bounding_box

    __or__ = union

    def intersection(self, *others):
        """
        Return the intersection of *self* and all the *boxes*.

        Usage:

        >>> from benker.box import Box
        >>> from benker.point import Point

        >>> b1 = Box(Point(3, 2), Point(6, 4))
        >>> b2 = Box(Point(4, 3), Point(5, 7))
        >>> b1.intersection(b2)
        Box(min=Point(x=4, y=3), max=Point(x=5, y=4))

        >>> b1 & b2
        Box(min=Point(x=4, y=3), max=Point(x=5, y=4))

        :param others: collections of boxes

        :return: The inner box of all the boxes.
        """
        boxes = (self,) + others
        min_list = tuple(box.min for box in boxes)
        min_pt = Point(max(pt.x for pt in min_list), max(pt.y for pt in min_list))
        max_list = tuple(box.max for box in boxes)
        max_pt = Point(min(pt.x for pt in max_list), min(pt.y for pt in max_list))
        inner_box = Box(min_pt, max_pt)
        assert all(inner_box in box for box in boxes)
        return inner_box

    __and__ = intersection

    # total ordering based on coordinates (*y* first, then *x*).
    # This or ordering can be used to sort boxes by rows and columns

    def __lt__(self, other):
        """
        Compare two boxes.

        Usage::

        >>> from benker.box import Box

        >>> b1 = Box(Point(3, 2), Point(6, 4))
        >>> b1 < b1
        False
        >>> b1 < Box(Point(3, 2), Point(6, 5))
        True
        >>> b1 < Box(Point(3, 2), Point(7, 4))
        True
        >>> b1 < Box(Point(4, 2), Point(6, 4))
        True
        >>> b1 < Box(Point(3, 3), Point(6, 4))
        True

        :param other: other box

        :return: ``True`` if *self* < *other*
        """
        if isinstance(other, Box):
            if self.min.y == other.min.y:
                if self.min.x == other.min.x:
                    if self.max.y == other.max.y:
                        return self.max.x < other.max.x
                    else:
                        return self.max.y < other.max.y
                else:
                    return self.min.x < other.min.x
            else:
                return self.min.y < other.min.y
        return NotImplemented
