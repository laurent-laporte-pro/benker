# coding: utf-8
"""
Office Open XML to Formex 4 converter
=====================================

.. versionchanged:: 0.5.0
   Refactoring (rename "Formex4" to "Formex"):

   - the class ``Ooxml2Formex4Converter`` is renamed ``Ooxml2FormexConverter``,
   - the function ``convert_ooxml2formex4`` is renamed ``convert_ooxml2formex``,
"""
from benker.builders.formex import FormexBuilder
from benker.converters.base_converter import BaseConverter
from benker.parsers.ooxml import OoxmlParser


class Ooxml2FormexConverter(BaseConverter):
    """
    Office Open XML to Formex 4 converter
    """
    parser_cls = OoxmlParser
    builder_cls = FormexBuilder


def convert_ooxml2formex(src_xml, dst_xml, **options):
    """
    Convert Office Open XML (OOXML) tables to Formex 4 tables.

    :param str src_xml:
        Source path of the XML file to convert.

        This must be an XML file, for instance, if you want to convert a Word
        document (``.docx``), you first need to unzip the ``.docx`` file, and
        then, run this function on the file ``word/document.xml``.
        You can also use the *styles_path* option to parse and use the table
        styles defined in the file ``word/styles.xml``.

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
    converter = Ooxml2FormexConverter()
    converter.convert_file(src_xml, dst_xml, **options)
