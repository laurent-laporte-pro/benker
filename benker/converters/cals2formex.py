# coding: utf-8
"""
CALS to Formex 4 converter
==========================

.. versionadded:: 0.5.0
"""


from benker.builders.formex import FormexBuilder
from benker.converters.base_converter import BaseConverter
from benker.parsers.cals import CalsParser


class Cals2FormexConverter(BaseConverter):
    """
    CALS to Formex 4 converter
    """

    parser_cls = CalsParser
    builder_cls = FormexBuilder


def convert_cals2formex(src_xml, dst_xml, **options):
    """
    Convert CALS 4 tables to Formex tables.

    :param str src_xml:
        Source path of the XML file to convert.

    :param str dst_xml:
        Destination path of the XML file to produce.

    :keywords options:
        Dictionary of parsing/building options.

        **Common parsing options:**

        ``encoding`` (default: "utf-8"):
            XML encoding of the destination file.

        **CALS parser options:**

        ``cals_ns`` (default ``None``):
            Namespace to use for CALS elements and attributes parsing.
            Set ``None`` (or "") if you don't use namespace in your XML.

        **Formex 4 builder options:**

        ``use_cals`` (default: ``False``):
            Generate additional CALS-like elements and attributes
            to simplify the layout of Formex document in typesetting systems.

        ``cals_ns`` (default: "https://lib.benker.com/schemas/cals.xsd"):
            Namespace to use for CALS-like elements and attributes (requires: ``use_cals``).
            Set ``None`` (or "") if you don't want to use namespace.

        ``cals_prefix`` (default: "cals"):
            Namespace prefix to use for CALS-like elements and attributes (requires: ``use_cals``).

        ``width_unit`` (default: "mm"):
            Unit to use for column widths (requires: ``use_cals``).
            Possible values are: 'cm', 'dm', 'ft', 'in', 'm', 'mm', 'pc', 'pt', 'px'.
    """
    converter = Cals2FormexConverter()
    converter.convert_file(src_xml, dst_xml, **options)
