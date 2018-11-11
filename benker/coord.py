# coding: utf-8
"""
Cell coord
========

Coordinates of a cell: tuple with *x*, *y* coordinates.
"""
import collections

from benker.alphabet import int_to_alphabet
from benker.size import Size


class Coord(collections.namedtuple('Coord', ['x', 'y'])):
    """
    Coordinates of a cell in a grid: *x* is the left column, *y* if the top row.

    Usage:

    >>> from benker.coord import Coord

    >>> coord = Coord(5, 3)
    >>> coord
    Coord(x=5, y=3)
    >>> str(coord)
    'E3'
    """
    __slots__ = ()

    def __str__(self):
        return int_to_alphabet(self.x) + str(self.y)

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
        Convert a value of type :class:`tuple` to a :class:`~benker.coord.Coord` object.

        :param value: tuple of two integers or *Coord* object.

        :return: Newly created object.
        """
        value_type = type(value)
        if value_type is cls:
            return value
        elif value_type is tuple and tuple(map(type, value)) == (int, int):
            return cls(*value)
        raise TypeError(repr(value_type))


PT_ORIGIN = Coord(1, 1)
