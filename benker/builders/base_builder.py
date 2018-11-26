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
        self.options = options

    def generate_table_tree(self, table):
        raise NotImplementedError
