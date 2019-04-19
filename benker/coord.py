# coding: utf-8
"""
Cell Coordinates
================

A :class:`~benker.coord.Coord` object is used to represent the *x* and *y* positions of a :class:`~benker.cell.Cell`.
The *x* is the left position (column number) and the *y* is the top position (row number).
The default cell coordinates is (1, 1).

This module defines the :class:`~benker.coord.Coord` tuple and give some classic use cases.
"""
import collections

from benker.alphabet import int_to_alphabet
from benker.size import Size

CoordTuple = collections.namedtuple('CoordTuple', ['x', 'y'])


class Coord(CoordTuple):
    """
    Coordinates of a cell in a grid: *x* is the left column, *y* if the top row.

    Usage:

    .. doctest:: coord_demo

        >>> from benker.coord import Coord

        >>> coord = Coord(5, 3)
        >>> coord
        Coord(x=5, y=3)
        >>> coord.x
        5
        >>> coord.y
        3
        >>> str(coord)
        'E3'

    You can use the "+" or "-" operators to move the coordinates:

    .. doctest:: coord_demo

        >>> from benker.size import Size

        >>> Coord(2, 1) + Size(3, 3)
        Coord(x=5, y=4)
        >>> Coord(5, 4) - Size(3, 3)
        Coord(x=2, y=1)

    .. warning::

        You cannot add or subtract two coordinates, only a coordinate and a size.

        .. doctest:: coord_demo

            >>> from benker.coord import Coord

            >>> Coord(2, 1) + Coord(3, 3)
            Traceback (most recent call last):
                ...
            TypeError: <class 'benker.coord.Coord'>
    """
    __slots__ = ()

    def __str__(self):
        return int_to_alphabet(self.x) + str(self.y)

    def __repr__(self):
        return super(Coord, self).__repr__().replace('CoordTuple', 'Coord')

    def __add__(self, size):
        size_type = type(size)
        if size_type is Size:
            return Coord(self.x + size.width, self.y + size.height)
        elif size_type is tuple:
            return Coord(self.x + size[0], self.y + size[1])
        elif size_type is int:
            return Coord(self.x + size, self.y + size)
        else:
            raise TypeError(repr(size_type))

    def __sub__(self, size):
        size_type = type(size)
        if size_type is Size:
            return Coord(self.x - size.width, self.y - size.height)
        elif size_type is tuple:
            return Coord(self.x - size[0], self.y - size[1])
        elif size_type is int:
            return Coord(self.x - size, self.y - size)
        else:
            raise TypeError(repr(size_type))

    @classmethod
    def from_value(cls, value):
        """
        Convert a value of type :class:`tuple` to a :class:`~benker.coord.Coord` tuple.

        :param value: tuple of two integers or :class:`~benker.coord.Coord` tuple.

        :return: Newly created object.

        :raises TypeError:
            if the value is not a tuple of integers nor a :class:`~benker.coord.Coord` tuple.
        """
        value_type = type(value)
        if value_type is cls:
            return value
        elif value_type is tuple and tuple(map(type, value)) == (int, int):
            return cls(*value)
        raise TypeError(repr(value_type))
