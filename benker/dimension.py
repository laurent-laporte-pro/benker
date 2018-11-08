# coding: utf-8
"""
Cell dimension
==============

Dimension of a cell: *width* is the number of columns and *height* is the number of row.
"""
import collections


class Dimension(collections.namedtuple('Dimension', ['width', 'height'])):
    """
    Dimension of a cell: *width* is the number of columns and *height* is the number of row.

    Usage:

    >>> from benker.dimension import Dimension

    >>> dim = Dimension(2, 1)
    >>> dim
    Dimension(width=2, height=1)
    >>> str(dim)
    '(2 x 1)'
    """
    __slots__ = ()

    def __str__(self):
        return "({width} x {height})".format(width=self.width, height=self.height)

    def __add__(self, dim):
        dim_type = type(dim)
        if dim_type is Dimension:
            return Dimension(self.width + dim.width, self.height + dim.height)
        elif dim_type is tuple:
            return Dimension(self.width + dim[0], self.height + dim[1])
        elif dim_type is int:
            return Dimension(self.width + dim, self.height + dim)
        else:
            raise TypeError(repr(dim_type))

    def __sub__(self, dim):
        dim_type = type(dim)
        if dim_type is Dimension:
            return Dimension(self.width - dim.width, self.height - dim.height)
        elif dim_type is tuple:
            return Dimension(self.width - dim[0], self.height - dim[1])
        elif dim_type is int:
            return Dimension(self.width - dim, self.height - dim)
        else:
            raise TypeError(repr(dim_type))

    def __mul__(self, dim):
        dim_type = type(dim)
        if dim_type is int:
            return Dimension(self.width * dim, self.height * dim)
        else:
            raise TypeError(repr(dim_type))

    def __neg__(self):
        return Dimension(-self.width, -self.height)

    def __pos__(self):
        return Dimension(self.width, self.height)
