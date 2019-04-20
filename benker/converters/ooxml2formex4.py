# coding: utf-8
"""
Office Open XML to Formex4 converter
====================================
"""
from benker.builders.formex4 import Formex4Builder
from benker.converters.base_converter import BaseConverter
from benker.parsers.ooxml import OoxmlParser


class Ooxml2Formex4Converter(BaseConverter):
    """
    Office Open XML to Formex4 converter
    """
    parser_cls = OoxmlParser
    builder_cls = Formex4Builder


def convert_ooxml2formex4(src_xml, dst_xml, **options):
    """
    Convert Office Open XML (OOXML) tables to Formex4 tables.

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
    converter = Ooxml2Formex4Converter()
    converter.convert_file(src_xml, dst_xml, **options)
