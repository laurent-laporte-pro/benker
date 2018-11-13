# coding: utf-8
"""
Styled object
=============

A :class:`benker.styled.Styled` object contains a dictionary of styles.

It is mainly used for :class:`~benker.table.Table`, :class:`~benker.row.Row`,
:class:`~benker.col.Col`, and :class:`~benker.cell.Cell`.

"""
import pprint


class Styled(object):
    """
    Styled object, like Table, Row, Column, or Cell objects.

    Styled object stores user-defined styles: a dictionary of key-value pairs.
    This values are useful to store some HTML-like styles (border-style,
    border-width, border-color, vertical-align, text-align, etc.).
    Of course, we are not tied to the HTML-like styles, you can use your
    own list of styles.

    .. note::

        The style dictionary is always copied: in other words, key-value pairs
        are copied but a shallow copy is done for the values (in general, it
        is not a problem if you use non-mutable values like :class:`str`).
    """
    __slots__ = ('_styles',)

    def __init__(self, styles=None):
        """
        Construct a styled object from a dictionary of styles.

        :type  styles: dict[str, str]
        :param styles:
            Dictionary of key-value pairs, where *keys* are the style names.
        """
        self.styles = styles

    def __str__(self):
        return str(self._styles)

    def __repr__(self):
        cls = self.__class__.__name__
        items = pprint.pformat(self._styles)
        return "<{cls}({items})>".format(cls=cls, items=items)

    @property
    def styles(self):
        """ Dictionary of styles: key-value pairs. """
        return self._styles

    @styles.setter
    def styles(self, styles):
        """ Setup the dictionary of styles (shallow copy of the items). """
        # each cell owns it's own copy of the styles
        self._styles = {} if styles is None else styles.copy()
