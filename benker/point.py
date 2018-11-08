# coding: utf-8
"""
Point
=====

Simple *Point* tuple with *x*, *y* coordinates.
"""
import collections

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


PT_ORIGIN = Point(1, 1)


class Dimension(collections.namedtuple('Dimension', ['width', 'height'])):
    """
    Dimension of a cell: *width* is the number of columns and *height* is the number of row.

    Usage:

    >>> from benker.point import Dimension

    >>> dim = Dimension(2, 1)
    >>> dim
    Dimension(width=2, height=1)
    >>> str(dim)
    '(2 x 1)'
    """
    __slots__ = ()

    def __str__(self):
        return "({width} x {height})".format(width=self.width, height=self.height)
