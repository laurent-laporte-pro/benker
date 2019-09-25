# coding: utf-8
"""
Formex 4 to CALS converter
==========================

.. versionadded:: 0.5.0
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

    :param str dst_xml:
        Destination path of the XML file to produce.

    :param str options:
        Dictionary of parsing/building options.

        **Common parsing options:**

        ``encoding`` (default: "utf-8"):
            XML encoding of the destination file.

        **Formex parser options:**

        ``formex_ns`` (default ``None``):
            Namespace to use for Formex elements and attributes parsing.
            Set ``None`` (or "") if you don't use namespace.

        ``cals_ns`` (default ``None``):
            Namespace to use for CALS-like elements and attributes parsing.
            Set ``None`` (or "") if you don't use namespace.

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
    """
    converter = Formex2CalsConverter()
    converter.convert_file(src_xml, dst_xml, **options)
