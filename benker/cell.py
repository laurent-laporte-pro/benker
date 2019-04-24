# coding: utf-8
"""
Grid Cell
=========

A :class:`~benker.cell.Cell` object stores the *content* of a :class:`~benker.grid.Grid` cell.

A cell can have *styles*, a dictionary of key-value properties attached to the cell.

A cell has a *nature* to distinguish between header, body and footer cells.
The default *nature* is "body", but you can also use "header", "footer" or whatever…

A cell has top-left coordinates: *x* and *y*. The default coordinates is (1, 1):
this is the top-left coordinate of the cell box.
The coordinates *x* and *y* cannot be null: grid coordinates are 1-indexed.

A cell has a size: *width* and *height*. The default size is (1, 1), you can
increase them to represent horizontal or vertical spanning.
The *width* and the *height* cannot be null.

.. doctest:: cell_demo
    :hide:

    >>> from benker.coord import Coord
    >>> from benker.box import Box
    >>> from benker.cell import Cell

To instantiate a :class:`~benker.cell.Cell`, you can do:

.. doctest:: cell_demo

    >>> c1 = Cell("c1")
    >>> c2 = Cell("c2", styles={'color': 'red'})
    >>> c3 = Cell("c3", nature="footer")
    >>> c4 = Cell("c4", width=2)
    >>> c5 = Cell("c5", height=2)

The string representation of a cell is the string representation of it's content:

.. doctest:: cell_demo

    >>> for cell in c1, c2, c3, c4, c5:
    ...     print(cell)
    c1
    c2
    c3
    c4
    c5

On initialization, the cell min position is always (1, 1), a.k.a. the top-left.

.. doctest:: cell_demo

    >>> c1 = Cell("c1")
    >>> c1.min
    Coord(x=1, y=1)
    >>> c1.size
    Size(width=1, height=1)
    >>> c1.box
    Box(min=Coord(x=1, y=1), max=Coord(x=1, y=1))

A cell can be moved to another position:

.. doctest:: cell_demo

    >>> c1 = Cell("c1", width=3, height=2)
    >>> c2 = c1.move_to(Coord(5, 3))
    >>> c2.min
    Coord(x=5, y=3)
    >>> c2.size
    Size(width=3, height=2)
    >>> c2.box
    Box(min=Coord(x=5, y=3), max=Coord(x=7, y=4))

You can check if a coord is inside the box:

.. doctest:: cell_demo

    >>> c1 = Cell("c1", width=3, height=2)
    >>> c2 = c1.move_to(Coord(5, 3))
    >>> (7, 4) in c2
    True
    >>> Coord(6, 3) in c2
    True
    >>> Box(6, 3, 7, 4) in c2
    True

"""
import functools
import sys

from benker.box import Box
from benker.styled import Styled

PY2 = sys.version_info[0] == 2

text_type = type(u"")
binary_type = type(b"")
string_types = text_type, binary_type


@functools.total_ordering
class Cell(Styled):
    """
    Cell of a grid.

    :ivar content: user-defined cell content. It can be of any type: ``None``,
        :class:`str`, :class:`int`, :class:`float`, a container (:class:`list`),
        a XML element, etc. The same content can be shared by several cells, it's
        your own responsibility to handle the copy (or deep copy) of the *content*
        reference when needed.

        .. note::

            In a :class:`~benker.grid.Grid`, the :ref:`merging <benker__grid__merging>`
            of two cell contents is done with the "+" operator (:func:`~operator.__add__`).
            You can override this by using a *content_appender*, a two-arguments
            function which will perform the concatenation of the two contents.

    :type styles: typing.Dict[str, str]
    :ivar styles: user-defined cell styles: a dictionary of key-value pairs.
        This values are useful to store some HTML-like styles (border-style,
        border-width, border-color, vertical-align, text-align, etc.).
        Of course, we are not tied to the HTML-like styles, you can use your own
        list of styles.

        .. note::

            The style dictionary is always copied: in other words, key-value pairs
            are copied but a shallow copy is done for the values (in general, it
            is not a problem if you use non-mutable values like :class:`str`).

    :type nature: str
    :ivar nature: nature: a way to distinguish the body cells, from the header and the footer.
        The default value is "body", but you can use "header", "footer" or whatever
        is suitable for your needs.

        .. note::

            In a :class:`~benker.grid.Grid`, the :ref:`merging <benker__grid__merging>`
            of two natures is done by keeping the first nature and
            dropping the second one. In other words, the resulting nature is
            the group of the most top-left nature of the merged cells.
    """
    __slots__ = ('content', '_box')

    def __init__(self, content, styles=None, nature="body", x=1, y=1, width=1, height=1):
        super(Cell, self).__init__(styles, nature)
        self.content = content
        self._box = Box(x, y, x + width - 1, y + height - 1)

    def __str__(self):
        """
        Try hard to extract a good string representation of the cell.

        :return: the cell text:

            - if the content is ``None``: returns "",
            - if the content is a string: return the string unchanged,
            - if the content is a number: return the string representation of the number,
            - if the content is a list of strings, return the concatenated strings (``None`` is ignored),
            - if the content is a list of XML nodes, return the concatenated strings of the elements
              (the processing-instruction and the comments are ignored),
            - else: return a concatenation of the string representation of the content items.

        .. versionchanged:: 0.4.1
           Improve the string representation of a cell in order to extract the cell text
           even if it contains a list of strings or XML nodes.
        """
        content = self.content
        if content is None:
            return u""
        if isinstance(content, text_type):
            return content
        if isinstance(content, binary_type):
            return content.decode('utf-8')  # PY2
        if isinstance(content, (bool, int, float)):
            return text_type(content)

        # We don't want to import lxml here, so we introspect the content.
        text = u""
        for node in content:
            if node is None:
                pass
            elif isinstance(node, text_type):
                text += node
            elif isinstance(node, binary_type):
                text += node.decode('utf-8')  # PY2
            elif hasattr(node, 'tag'):
                tag = node.tag
                if isinstance(tag, string_types):
                    # etree._Element
                    text += node.xpath('string()')
                else:
                    # ignore: etree._ProcessingInstruction or etree._Comment
                    pass
            else:
                text += text_type(node)
        return text

    if PY2:
        __unicode__ = __str__

        def __str__(self):
            return self.__unicode__().encode('ascii', errors='backslashreplace')

    def __repr__(self):
        cls = self.__class__.__name__
        return ("<{cls}({self.content!r}, "
                "styles={self.styles!r}, "
                "nature={self.nature!r}, "
                "x={self.min.x!r}, "
                "y={self.min.y!r}, "
                "width={self.width!r}, "
                "height={self.height!r})>"
                .format(cls=cls, self=self))

    @property
    def box(self):
        """ Bounding box of the cell. """
        return self._box

    @property
    def min(self):
        """ Minimum coordinates of the cell -- top-left coordinates. """
        return self.box.min

    @property
    def max(self):
        """ Maximum coordinates of the cell -- bottom-right coordinates. """
        return self.box.max

    @property
    def size(self):
        """ Size of the cell -- (*with*, *height*). """
        return self.box.size

    @property
    def width(self):
        """ Width of the cell -- columns spanning. """
        return self.box.width

    @property
    def height(self):
        """ Height of the cell -- rows spanning. """
        return self.box.height

    def __contains__(self, other):
        return other in self.box

    # total ordering based on Box ordering

    def __lt__(self, other):
        if isinstance(other, Cell):
            return self.box < other.box
        elif isinstance(other, Box):
            return self.box < other
        return NotImplemented

    def transform(self, coord=None, size=None):
        """
        Transform the bounding box of the cell by making a move and a resize.

        :type  coord: tuple[int, int] or benker.coord.Coord
        :param coord: new top-left coordinates of the cell, by default it is unchanged.

        :type  size: tuple[int, int] or benker.size.Size
        :param size: new size of the cell, by default it is unchanged.

        :rtype: benker.cell.Cell
        :return: a copy of this cell after transformation.
        """
        box = self.box.transform(coord=coord, size=size)
        cell = Cell(self.content,
                    styles=self.styles,
                    nature=self.nature,
                    x=box.min.x,
                    y=box.min.y,
                    width=box.width,
                    height=box.height)
        return cell

    def move_to(self, coord):
        """
        Move the cell to the given coordinates.

        See: :meth:`~benker.cell.Cell.transform`.

        :type  coord: tuple[int, int] or benker.coord.Coord
        :param coord: new top-left coordinates of the cell, by default it is unchanged.

        :rtype: benker.cell.Cell
        :return: a copy of this cell after transformation.
        """
        return self.transform(coord=coord)

    def resize(self, size):
        """
        Resize the cell to the given size.

        See: :meth:`~benker.cell.Cell.transform`.

        :type  size: tuple[int, int] or benker.size.Size
        :param size: new size of the cell, by default it is unchanged.

        :rtype: benker.cell.Cell
        :return: a copy of this cell after transformation.
        """
        return self.transform(size=size)
