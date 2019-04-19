# coding: utf-8
u"""
Box
===

A *Box* is a rectangular area defined by two coordinates:

- the top-left corner of the rectangle: the *min* coord,
- the bottom-right corner of the rectangle: the *max* coord.

.. doctest:: box_demo
    :hide:

    >>> from benker.box import Box
    >>> from benker.coord import Coord

To instantiate a :class:`~benker.box.Box`, you can do:

.. doctest:: box_demo

    >>> b1 = Box(Coord(5, 6), Coord(7, 8))
    >>> b2 = Box(Coord(5, 6))
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

You can calculate the *width* and *height* of boxes:

.. doctest:: box_demo

    >>> b1 = Box(Coord(5, 6), Coord(6, 8))
    >>> b1.width, b1.height
    (2, 3)

    >>> b2 = Box(Coord(5, 6))
    >>> b2.width, b2.height
    (1, 1)

You can determine if a *Coord* is included in a *Box*:

.. doctest:: box_demo

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

You can determine if two boxes intersect each other, or are disjoints:

.. doctest:: box_demo

    >>> b1 = Box(Coord(5, 6), Coord(6, 8))
    >>> b2 = Box(Coord(6, 6), Coord(6, 7))
    >>> b3 = Box(Coord(7, 6), Coord(7, 8))
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

from benker.coord import Coord
from benker.size import Size

BoxTuple = collections.namedtuple('BoxTuple', ['min', 'max'])


@functools.total_ordering
class Box(BoxTuple):
    """
    A *Box* is a rectangular area defined by two coordinates:

    - the top-left corner of the rectangle: the *min* coord,
    - the bottom-right corner of the rectangle: the *max* coord.

    Usage:

    .. doctest:: box_demo

        >>> from benker.box import Box

        >>> box = Box(1, 1, 5, 3)
        >>> box
        Box(min=Coord(x=1, y=1), max=Coord(x=5, y=3))

    """
    __slots__ = ()

    def __new__(cls, *args):
        """
        Construct a new *Box*.

        :param args:
            Arguments could be:

            - top-left and bottom-right coordinates of the box: Coord(*min_coord*, *max_coord*);
            - top-left coordinates and box size: Coord(*min_coord*, *max_coord*), Size(*width*, *height*);
            - top-left coordinates of the box: Coord(*min_coord*, *max_coord*),
              assuming box size is (1, 1),
            - coordinates of the box: *min_x*, *min_y*, *max_x*, *max_y*;
            - coordinates of the top-left coord: *min_x*, *min_y*,
              assuming box size is (1, 1);
            - another box.

        :return: The new *Box*.

        :raises TypeError:
            if the arguments are of incompatible types.

        :raises ValueError:
        """
        types = tuple(map(type, args))
        if types == (Coord, Coord):
            min_x, min_y = args[0]
            max_x, max_y = args[1]
        elif types == (Coord, Size):
            min_x, min_y = args[0]
            max_x, max_y = args[0] + args[1] - 1
        elif types == (Coord,):
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
            min_coord = Coord(min_x, min_y)
            max_coord = Coord(max_x, max_y)
            # noinspection PyArgumentList
            return super(Box, cls).__new__(cls, min_coord, max_coord)
        raise ValueError(*args)

    def __str__(self):
        if (self.width, self.height) == (1, 1):
            return str(self.min)
        return str(self.min) + ':' + str(self.max)

    def __repr__(self):
        return super(Box, self).__repr__().replace('BoxTuple', 'Box')

    @property
    def width(self):
        # type: () -> int
        return self.max.x - self.min.x + 1

    @property
    def height(self):
        # type: () -> int
        return self.max.y - self.min.y + 1

    @property
    def size(self):
        return Size(self.width, self.height)

    def transform(self, coord=None, size=None):
        min_coord = self.min if coord is None else Coord.from_value(coord)
        size = self.size if size is None else Size.from_value(size)
        max_coord = min_coord + size - 1
        return Box(min_coord, max_coord)

    def move_to(self, coord):
        return self.transform(coord=coord)

    def resize(self, size):
        return self.transform(size=size)

    def __contains__(self, coord):
        coord_type = type(coord)
        if coord_type is Coord:
            return self.min.x <= coord.x <= self.max.x and self.min.y <= coord.y <= self.max.y
        elif coord_type is tuple and tuple(map(type, coord)) == (int, int):
            return self.min.x <= coord[0] <= self.max.x and self.min.y <= coord[1] <= self.max.y
        elif coord_type is Box:
            return coord.min in self and coord.max in self
        raise TypeError(repr(coord_type))

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

        .. doctest:: box_demo

            >>> from benker.box import Box
            >>> from benker.coord import Coord

            >>> b1 = Box(Coord(3, 2), Coord(6, 4))
            >>> b2 = Box(Coord(4, 3), Coord(5, 7))
            >>> b1.union(b2)
            Box(min=Coord(x=3, y=2), max=Coord(x=6, y=7))

            >>> b1 | b2
            Box(min=Coord(x=3, y=2), max=Coord(x=6, y=7))

        :param others: collections of boxes

        :return: The bounding box of all the boxes.
        """
        boxes = (self,) + others
        min_list = tuple(box.min for box in boxes)
        min_coord = Coord(min(coord.x for coord in min_list), min(coord.y for coord in min_list))
        max_list = tuple(box.max for box in boxes)
        max_coord = Coord(max(coord.x for coord in max_list), max(coord.y for coord in max_list))
        bounding_box = Box(min_coord, max_coord)
        assert all(box in bounding_box for box in boxes)
        return bounding_box

    __or__ = union

    def intersection(self, *others):
        """
        Return the intersection of *self* and all the *boxes*.

        Usage:

        .. doctest:: box_demo

            >>> from benker.box import Box
            >>> from benker.coord import Coord

            >>> b1 = Box(Coord(3, 2), Coord(6, 4))
            >>> b2 = Box(Coord(4, 3), Coord(5, 7))
            >>> b1.intersection(b2)
            Box(min=Coord(x=4, y=3), max=Coord(x=5, y=4))

            >>> b1 & b2
            Box(min=Coord(x=4, y=3), max=Coord(x=5, y=4))

        :param others: collections of boxes

        :return: The inner box of all the boxes.

        :raises ValueError: if the two boxes are disjoint.
        """
        boxes = (self,) + others
        min_list = tuple(box.min for box in boxes)
        min_coord = Coord(max(coord.x for coord in min_list), max(coord.y for coord in min_list))
        max_list = tuple(box.max for box in boxes)
        max_coord = Coord(min(coord.x for coord in max_list), min(coord.y for coord in max_list))
        try:
            return Box(min_coord, max_coord)
        except ValueError:
            # the two boxes are disjoint
            raise ValueError(boxes)

    __and__ = intersection

    # total ordering based on coordinates (*y* first, then *x*).
    # This or ordering can be used to sort boxes by rows and columns

    def __lt__(self, other):
        """
        Compare two boxes.

        Usage::

        .. doctest:: box_demo

            >>> from benker.box import Box

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
