# coding: utf-8
"""
Office Open XML to CALS converter
=================================
"""
from benker.builders.cals import CalsBuilder
from benker.converters.base_converter import BaseConverter
from benker.parsers.ooxml import OoxmlParser


class Ooxml2CalsConverter(BaseConverter):
    """
    Office Open XML to CALS converter
    """

    parser_cls = OoxmlParser
    builder_cls = CalsBuilder


def convert_ooxml2cals(src_xml, dst_xml, **options):
    """
    Convert Office Open XML (OOXML) tables to CALS tables.

    :param str src_xml:
        Source path of the XML file to convert.

        This must be an XML file, for instance, if you want to convert a Word
        document (``.docx``), you first need to unzip the ``.docx`` file, and
        then, run this function on the file ``word/document.xml``.
        You can also use the *styles_path* option to parse and use the table
        styles defined in the file ``word/styles.xml``.

    :param str dst_xml:
        Destination path of the XML file to produce.

    :keyword options:
        Dictionary of parsing/building options.

        **Common parsing options:**

        ``encoding`` (default: "utf-8"):
            XML encoding of the destination file.

        **OOXML parser options:**

        ``styles_path`` (default: ``None``):
            Path to the stylesheet to use to resole table styles.
            In an uncompressed ``.docx`` tree structure, the stylesheet path
            is ``word/styles.xml``.

        **CALS builder options:**

        ``cals_ns`` (default: ``None``):
            Namespace to use for CALS-like elements and attributes to generate.
            Set ``None`` (or "") if you don't want to use namespace.

        ``cals_prefix`` (default: ``None``):
            Namespace prefix to use for CALS-like elements and attributes to generate.

        ``width_unit`` (default: "mm"):
            Unit to use for column widths.
            Possible values are: 'cm', 'dm', 'ft', 'in', 'm', 'mm', 'pc', 'pt', 'px'.

        ``table_in_tgroup`` (default: ``False``):
            Where should we put the table properties:

            -   ``False`` to insert the attributes ``@colsep``, ``@rowsep``,
                and ``@tabstyle`` in the ``<table>`` element,

            -   ``True`` to insert the attributes ``@colsep``, ``@rowsep``,
                and ``@tgroupstyle`` in the ``<tgroup>`` element.

        ``tgroup_sorting`` (default: ``["header", "footer", "body"]``):
            List used to sort (and group) the rows in a ``tgroup``.
            The sorting is done according to the row natures
            which is by default: ``["header", "footer", "body"]``
            (this order match the CALS DTD defaults,
            where the footer is between the header and the body.
            To move the footer to the end, you can use ``["header", "body", "footer"]``.

    .. versionchanged:: 0.5.0
       Add the options *cals_ns*, *cals_prefix*, *tgroup_sorting*.
    """
    converter = Ooxml2CalsConverter()
    converter.convert_file(src_xml, dst_xml, **options)
