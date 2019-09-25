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

    def convert_file(self, src_xml, dst_xml, **options):
        """
        Convert the tables from one format to another.

        :param str src_xml:
            Source path of the XML file to convert.

        :param str dst_xml:
            Destination path of the XML file to produce.

        :keywords options:
            Dictionary of parsing/building options.

            **Common parsing options:**

            ``encoding`` (default: "utf-8"):
                XML encoding of the destination file.
        """
        builder = self.builder_cls(**options)
        parser = self.parser_cls(builder, **options)
        parser.parse_file(src_xml, dst_xml)
