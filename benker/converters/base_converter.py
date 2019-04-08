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

        :param str options:
            Dictionary of parsing/building options.

            **Common parsing options:**

            ``encoding`` (default: "utf-8"):
                XML encoding of the destination file.

            **OOXML parser options:**

            ``styles_path`` (default: ``None``):
                Path to the stylesheet to use to resole table styles.
                In an uncompressed ``.docx`` tree structure, the stylesheet path
                is ``word/styles.xml``.

            **Common builder options:** *(none)*

            **CALS builder options:**

            ``width_unit`` (default: "mm"):
                Unit to use for column widths.
                Possible values are: 'cm', 'dm', 'ft', 'in', 'm', 'mm', 'pc', 'pt', 'px'.

            ``table_in_tgroup`` (default: ``False``):
                Where should we put the table properties:

                -   ``False`` to insert the attributes ``@colsep``, ``@rowsep``,
                    and ``@tabstyle`` in the ``<table>`` element,

                -   ``True`` to insert the attributes ``@colsep``, ``@rowsep``,
                    and ``@tgroupstyle`` in the ``<tgroup>`` element.

            **Formex4 builder options:** *(none)*

        """
        builder = self.builder_cls(**options)
        parser = self.parser_cls(builder, **options)
        parser.parse_file(src_xml, dst_xml)
