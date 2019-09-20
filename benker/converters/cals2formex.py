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

    :param str options: Extra conversion options.
        See :meth:`~benker.converters.base_converter.BaseConverter.convert_file`
        to have a list of all possible options.
    """
    converter = Cals2FormexConverter()
    converter.convert_file(src_xml, dst_xml, **options)
