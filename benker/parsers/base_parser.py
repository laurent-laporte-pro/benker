# coding: utf-8
"""
Base Parser
===========

Base class of parsers.
"""
import collections

from lxml import etree


class BaseParser(object):
    """
    Abstract base class of the parsers classes.
    """

    class _State(object):
        """
        Parsing state for the converter (internal usage).
        """

        def __init__(self):
            self.col_pos = 0
            self.col = None
            self.row_pos = 0
            self.row = None
            self.table = None

        reset = __init__

        def next_col(self):
            self.col_pos += 1
            self.col = None

        def next_row(self):
            self.col_pos = 0
            self.col = None
            self.row_pos += 1
            self.row = None

    def __init__(self, builder, encoding="utf-8", **options):
        """
        Construct a base builder.

        :type  builder: benker.builders.base_builder.BaseBuilder
        :param builder:
            Builder used by this parser to instantiate :class:`~benker.table.Table` objects.

        :param str encoding:
            XML encoding of the destination file (default: "utf-8").

        :param str options: Extra conversion options.
            See :meth:`~benker.converters.base_converter.BaseConverter.convert_file`
            to have a list of all possible options.
        """
        self.builder = builder
        self.encoding = encoding
        self.options = options
        self._state = self._State()

    def parse_file(self, src_xml, dst_xml):
        tree = etree.parse(src_xml)
        self.transform_tables(tree)
        self.builder.finalize_tree(tree)
        tree.write(dst_xml, encoding=self.encoding, pretty_print=False)

    def transform_tables(self, tree):
        raise NotImplementedError


def value_of(element, xpath, namespaces=None, default=None):
    """
    Take the first value of a xpath evaluation.

    :type  element: etree._Element
    :param element: Root element used to evaluate the xpath expression.

    :param str xpath: xpath expression.
        This expression will be evaluated using the *namespaces* namespaces.

    :type  namespaces: dict[str, str]
    :param namespaces:
        Namespace map to use for the xpath evaluation.

    :param default: default value used if the xpath evaluation returns no result.

    :return: the first result or the *default* value.
    """
    if element is None:
        return default
    nodes = element.xpath(xpath, namespaces=namespaces)
    return nodes[0] if nodes else default


class Namespace(collections.namedtuple("Namespace", "prefix, uri")):
    """
    A namespace is defined by a *prefix* and an *uri*.
    """
    def get_qname(self, name):
        """ get the qualified name """
        return etree.QName(self.uri, name)

    def get_name(self, name):
        """ get the prefixed name """
        fmt = "{prefix}:{name}" if self.prefix else "{name}"
        return fmt.format(prefix=self.prefix, name=name)
