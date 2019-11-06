# coding: utf-8
"""
Base Builder
============

Base class of Builders.
"""
import numbers

from lxml import etree

try:
    # noinspection PyCompatibility
    from collections.abc import Sequence
except ImportError:
    # noinspection PyCompatibility
    from collections import Sequence


text_type = type(u"")
binary_type = type(b"")
string_types = text_type, binary_type

# noinspection PyProtectedMember
#: Element Type
ElementType = etree._Element


class BaseBuilder(object):
    """
    Base class of Builders.
    """

    def __init__(self, **options):
        """
        Construct a builder.

        :param options: building options.
        """
        self.options = options

    def generate_table_tree(self, table):
        """
        Build the XML table from the Table instance.

        :type  table: benker.table.Table
        :param table: Table

        :return: Table tree
        """
        raise NotImplementedError

    def finalize_tree(self, tree):
        """
        Give the opportunity to finalize the resulting tree structure.

        :param tree: The resulting tree.

        .. versionadded:: 0.4.0
        """

    @staticmethod
    def append_cell_elements(cell_elem, elements):
        """
        Append XML elements, PIs or texts to a cell element.

        :type  cell_elem: ElementType
        :param cell_elem: Cell element

        :param elements: list of child elements to append

        .. versionadded:: 0.5.1
        """
        if elements is None:
            cell_elem.text = elements
        elif isinstance(elements, text_type):
            cell_elem.text = elements
        elif isinstance(elements, binary_type):
            cell_elem.text = elements.decode('utf-8')  # PY2
        elif isinstance(elements, numbers.Number):
            cell_elem.text = text_type(elements)
        elif isinstance(elements, ElementType):
            cell_elem.append(elements)
        elif isinstance(elements, Sequence):
            for node in elements:
                if isinstance(node, ElementType):
                    cell_elem.append(node)
                elif len(cell_elem) == 0:
                    text = cell_elem.text or ""
                    cell_elem.text = text + node
                else:
                    last_elem = cell_elem[-1]
                    tail = last_elem.tail or ""
                    last_elem.tail = tail + node
        else:  # pragma: no cover
            raise TypeError(repr(elements))
