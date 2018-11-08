# coding: utf-8
"""
Point
=====

Simple *Point* tuple with *x*, *y* coordinates.
"""
import collections

from benker.dimension import Dimension
from benker.utils import int_to_alphabet


class Point(collections.namedtuple('Point', ['x', 'y'])):
    """
    Coordinates of a cell in a grid: *x* is the left column, *y* if the top row.

    Usage:

    >>> from benker.point import Point

    >>> pt = Point(5, 3)
    >>> pt
    Point(x=5, y=3)
    >>> str(pt)
    'E3'
    """
    __slots__ = ()

    def __str__(self):
        return int_to_alphabet(self.x) + str(self.y)

    def __add__(self, dim):
        dim_type = type(dim)
        if dim_type is Dimension:
            return Point(self.x + dim.width, self.y + dim.height)
        elif dim_type is tuple:
            return Point(self.x + dim[0], self.y + dim[1])
        elif dim_type is int:
            return Point(self.x + dim, self.y + dim)
        else:
            raise TypeError(repr(dim_type))

    def __sub__(self, dim):
        dim_type = type(dim)
        if dim_type is Dimension:
            return Point(self.x - dim.width, self.y - dim.height)
        elif dim_type is tuple:
            return Point(self.x - dim[0], self.y - dim[1])
        elif dim_type is int:
            return Point(self.x - dim, self.y - dim)
        else:
            raise TypeError(repr(dim_type))


PT_ORIGIN = Point(1, 1)
