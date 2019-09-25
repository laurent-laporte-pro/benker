.. _benker__converters__formex__cals:

Formex 4 to CALS converter
==========================

Description
-----------

.. _Formex 4 format: https://publications.europa.eu/en/web/eu-vocabularies/formex
.. _CALS table format: https://www.oasis-open.org/specs/a502.htm

The :func:`~benker.converters.formex2cals.convert_formex2cals` converter is a function designed to convert tables from an Formex 4 document (which respects the schema defined in `Formex 4 format`_) in the `CALS table format`_.

The conversion is done in the source XML document by replacing the tables of the Formex 4 format with those transformed in the CALS format.
In other words, the general structure of the source XML document is retained except for tables.

The :class:`~benker.converters.formex2cals.Formex2CalsConverter` converter is composed of:

*   a :class:`~benker.parsers.formex.FormexParser` parser that allows you to parse tables in Formex 4 format,

    The tutorial :ref:`benker__parsers__formex` describes the usage of this parser and gives some examples.

*   a :class:`~benker.builders.formex.CalsBuilder` builder that allows you to build tables in the CALS format.

    The tutorial :ref:`benker__builders__cals` describes the usage of this builder and gives some examples.

Conversion options
------------------

The tables parsing and building can be parameterized using the options described below:

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

``tgroup_sorting`` (default: ``["header", "footer", "body"]``):
    List used to sort (and group) the rows in a ``tgroup``.
    The sorting is done according to the row natures
    which is by default: ``["header", "footer", "body"]``
    (this order match the CALS DTD defaults,
    where the footer is between the header and the body.
    To move the footer to the end, you can use ``["header", "body", "footer"]``.

Examples of conversions
-----------------------

