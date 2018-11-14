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

    A styled object stores user-defined styles: a dictionary of key-value pairs.
    This values are useful to store some HTML-like styles (border-style,
    border-width, border-color, vertical-align, text-align, etc.).
    Of course, we are not tied to the HTML-like styles, you can use your
    own list of styles.

    .. note::

        The style dictionary is always copied: in other words, key-value pairs
        are copied but a shallow copy is done for the values (in general, it
        is not a problem if you use non-mutable values like :class:`str`).

    A styled object stores a cell group: a way to distinguish the body cells,
    from the header and the footer. The default value is "body", but you can
    use "header", "footer" or whatever is suitable for your needs.
    This kind of information is in general not stored in the styles,
    even if it is similar.

    .. note::

        In a :class:`~benker.grid.Grid`, the :ref:`merging <benker__grid__merging>`
        of two cell groups is done by keeping the first cell group and
        dropping the second one. In other words, the resulting cell group is
        the group of the most top-left cell group of the merged cells.

    """
    __slots__ = ('_styles', 'cell_group')

    def __init__(self, styles, cell_group):
        """
        Construct a styled object from a dictionary of styles.

        :type  styles: typing.Dict[str, str]
        :param styles:
            Dictionary of key-value pairs, where *keys* are the style names.

        :type cell_group: str
        :ivar cell_group:
            Cell group: a way to distinguish the body cells, from the header and the footer.
        """
        self.styles = styles
        self.cell_group = cell_group

    def __str__(self):
        return str(self._styles)

    def __repr__(self):
        cls = self.__class__.__name__
        items = pprint.pformat(self._styles)
        cell_group = self.cell_group
        return "<{cls}({items}, {cell_group!r})>".format(cls=cls, items=items, cell_group=cell_group)

    @property
    def styles(self):
        """ Dictionary of styles: key-value pairs. """
        return self._styles

    @styles.setter
    def styles(self, styles):
        """ Setup the dictionary of styles (shallow copy of the items). """
        # each cell owns it's own copy of the styles
        self._styles = {} if styles is None else styles.copy()
