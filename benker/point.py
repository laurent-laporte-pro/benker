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
    Simple *Point* tuple with *x*, *y* coordinates.

    Usage:

    >>> from benker.point import Point

    >>> p = Point(5, 3)
    >>> p
    Point(x=5, y=3)
    >>> str(p)
    'E3'
    """
    __slots__ = ()

    def __str__(self):
        return int_to_alphabet(self.x) + str(self.y)
