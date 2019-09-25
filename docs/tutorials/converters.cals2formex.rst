CALS to Formex 4 converter
==========================

Description
-----------

.. _Formex 4 format: https://publications.europa.eu/en/web/eu-vocabularies/formex
.. _CALS table format: https://www.oasis-open.org/specs/a502.htm

The :func:`~benker.converters.cals2formex.convert_cals2formex` converter is a function designed to convert tables from an CALS document (which respects the schema defined in `CALS table format`_) in the `Formex 4 format`_.

The conversion is done in the source XML document by replacing the tables of the CALS format with those transformed in the Formex 4 format.
In other words, the general structure of the source XML document is retained except for tables.

The :class:`~benker.converters.cals2formex.Cals2FormexConverter` converter is composed of:

*   a :class:`~benker.parsers.cals.CalsParser` parser that allows you to parse tables in CALS format,

    The tutorial :ref:`benker__parsers__cals` describes the usage of this parser and gives some examples.

*   a :class:`~benker.builders.cals.FormexBuilder` builder that allows you to build tables in the Formex 4 format.

    The tutorial :ref:`benker__builders__formex` describes the usage of this builder and gives some examples.

Conversion options
------------------

The tables parsing and building can be parameterized using the options described below:

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

Examples of conversions
-----------------------

