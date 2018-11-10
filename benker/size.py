# coding: utf-8
"""
Cell size
=========

Size of a cell: *width* is the number of columns and *height* is the number of row.
"""
import collections


class Size(collections.namedtuple('Size', ['width', 'height'])):
    """
    Size of a cell: *width* is the number of columns and *height* is the number of row.

    Usage:

    >>> from benker.size import Size

    >>> size = Size(2, 1)
    >>> size
    Size(width=2, height=1)
    >>> str(size)
    '(2 x 1)'
    """
    __slots__ = ()

    def __str__(self):
        return "({width} x {height})".format(width=self.width, height=self.height)

    def __add__(self, size):
        size_type = type(size)
        if size_type is Size:
            return Size(self.width + size.width, self.height + size.height)
        elif size_type is tuple:
            return Size(self.width + size[0], self.height + size[1])
        elif size_type is int:
            return Size(self.width + size, self.height + size)
        else:
            raise TypeError(repr(size_type))

    def __sub__(self, size):
        size_type = type(size)
        if size_type is Size:
            return Size(self.width - size.width, self.height - size.height)
        elif size_type is tuple:
            return Size(self.width - size[0], self.height - size[1])
        elif size_type is int:
            return Size(self.width - size, self.height - size)
        else:
            raise TypeError(repr(size_type))

    def __mul__(self, size):
        size_type = type(size)
        if size_type is int:
            return Size(self.width * size, self.height * size)
        else:
            raise TypeError(repr(size_type))

    def __neg__(self):
        return Size(-self.width, -self.height)

    def __pos__(self):
        return Size(self.width, self.height)
