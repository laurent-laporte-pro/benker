# coding: utf-8
"""
Base Builder
============

Base class of Builders.
"""


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

        :type  tree: etree._ElementTree
        :param tree: The resulting tree.

        .. versionadded:: 0.4.0
        """
