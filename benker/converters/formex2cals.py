# coding: utf-8
"""
Formex 4 to CALS converter
==========================
"""


from benker.builders.cals import CalsBuilder
from benker.converters.base_converter import BaseConverter
from benker.parsers.formex import FormexParser


class Formex2CalsConverter(BaseConverter):
    """
    Formex 4 to CALS converter
    """
    parser_cls = FormexParser
    builder_cls = CalsBuilder


def convert_formex2cals(src_xml, dst_xml, **options):
    """
    Convert Formex 4 tables to Cals tables.

    :param str src_xml:
        Source path of the XML file to convert.

        This must be an XML file, for instance, if you want to convert a Word
        document (``.docx``), you first need to unzip the ``.docx`` file, and
        then, run this function on the file ``word/document.xml``.
        You can also use the *styles_path* option to parse and use the table
        styles defined in the file ``word/styles.xml``.

    :param str dst_xml:
        Destination path of the XML file to produce.

    :param str options: Extra conversion options.
        See :meth:`~benker.converters.base_converter.BaseConverter.convert_file`
        to have a list of all possible options.
    """
    converter = Formex2CalsConverter()
    converter.convert_file(src_xml, dst_xml, **options)
