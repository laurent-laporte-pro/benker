# coding: utf-8
"""
Base Converter
==============

Bas class of all converters.
"""
from benker.builders.base_builder import BaseBuilder
from benker.parsers.base_parser import BaseParser


class BaseConverter(object):
    """
    Bas class of all converters.
    """
    parser_cls = BaseParser
    builder_cls = BaseBuilder

    def __init__(self):
        self.parser = None

    def convert_file(self, src_xml, dst_xml, **options):
        builder = self.builder_cls(**options)
        parser = self.parser_cls(builder, **options)
        parser.parse_file(src_xml, dst_xml)
