# coding: utf-8
"""
Cell Size
=========

A :class:`~benker.size.Size` object is used to represent the *width* and *height* of a :class:`~benker.cell.Cell`.
The *width* is the number of spanned columns and the *height* is the number of spanned rows.
The default cell size is (1, 1).

This module defines the :class:`~benker.size.Size` tuple and give some classic use cases.
"""
import collections

SizeTuple = collections.namedtuple('SizeTuple', ['width', 'height'])


class Size(SizeTuple):
    """
    Size of a cell: *width* is the number of columns and *height* is the number of row.

    Usage:

    >>> from benker.size import Size

    >>> size = Size(2, 1)
    >>> size
    Size(width=2, height=1)
    >>> size.width
    2
    >>> size.height
    1
    >>> str(size)
    '(2 x 1)'

    You can use the "+" or "-" operators to increase or decrease the size:

    >>> Size(2, 1) + Size(3, 3)
    Size(width=5, height=4)
    >>> Size(5, 4) - Size(3, 3)
    Size(width=2, height=1)

    You can expand the *width* and *height* to a given factor using the "*" operator:

    >>> Size(2, 1) * 2
    Size(width=4, height=2)

    You can have negative or positive sizes using the unary operators "-" and "+":

    >>> +Size(3, 2)
    Size(width=3, height=2)
    >>> -Size(3, 2)
    Size(width=-3, height=-2)

    .. note::

       A :class:`~benker.cell.Cell` object cannot have a negative or nul sizes,
       but you can need this values for calculation, for instance when you want to
       reduce the cell size.
    """
    __slots__ = ()

    def __str__(self):
        return "({width} x {height})".format(width=self.width, height=self.height)

    def __repr__(self):
        return super(Size, self).__repr__().replace('SizeTuple', 'Size')

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

    @classmethod
    def from_value(cls, value):
        """
        Convert a value of type :class:`tuple` to a :class:`~benker.size.Size` tuple.

        :param value: tuple of two integers or :class:`~benker.size.Size` tuple.

        :return: Newly created object.

        :raises TypeError:
            if the value is not a tuple of integers nor a :class:`~benker.size.Size` tuple.
        """
        value_type = type(value)
        if value_type is cls:
            return value
        elif value_type is tuple and tuple(map(type, value)) == (int, int):
            return cls(*value)
        raise TypeError(repr(value_type))
