# coding: utf-8
"""
Cell coord
========

Coordinates of a cell: tuple with *x*, *y* coordinates.
"""
import collections

from benker.size import Size
from benker.alphabet import int_to_alphabet


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


PT_ORIGIN = Coord(1, 1)
