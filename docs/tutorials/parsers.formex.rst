.. _benker__parsers__formex:

Formex 4 tables parser
======================

Description
-----------

A :class:`~benker.parsers.formex.FormexParser` is used to parse the tables (actually, it parses ``CORPUS`` elements) of a Formex 4 document and generate a :class:`~benker.table.Table` instances (memory representation of a table).
The instance can then be serialize in another XML format, like CALS.

To use this class, you need to inherit the :class:`~benker.builders.base_builder.BaseBuilder` class
and create an instance of your class to used in the :class:`~benker.parsers.formex.FormexParser` parser.

Of course, for the sake of this demonstration we can used an instance
of the class :class:`~benker.builders.base_builder.BaseBuilder`, without implementing
the :meth:`~benker.builders.base_builder.BaseBuilder.generate_table_tree` method.

.. doctest:: parsers__formex

    >>> from lxml import etree
    >>> from benker.builders.base_builder import BaseBuilder
    >>> from benker.parsers.formex import FormexParser

    >>> builder = BaseBuilder()
    >>> parser = FormexParser(builder)

For example, you can parse the following Formex 4 table:

.. literalinclude:: parsers.formex.sample1.xml
   :language: xml
   :encoding: utf-8

And generate a :class:`~benker.table.Table` instance:

.. doctest:: parsers__formex

    >>> tree = etree.parse("docs/tutorials/parsers.formex.sample1.xml")
    >>> fmx_table = tree.getroot()
    >>> table = parser.parse_table(fmx_table)
    >>> print(table)
    +-----------+-----------------------------------------------+-----------------------------------+-----------+
    |           |             Identific                         |             Condition             |           |
    +-----------+-----------+-----------+-----------+-----------+-----------+-----------+-----------+-----------+
    | Numéro d’ | Nom chimi | Dénominat | Numéro CA | Numéro CE | Type de p | Concentra |  Autres   | Libellé d |
    +-----------+-----------+-----------+-----------+-----------+-----------+-----------+-----------+-----------+
    |     a     |     b     |     c     |     d     |     e     |     f     |     g     |     h     |     i     |
    +-----------+-----------+-----------+-----------+-----------+-----------+-----------+-----------+-----------+
    |    31     | 3,3'-(1,4 | phénylène | 55514-22- | 700-823-1 |           |    5 %    | Ne pas ut |           |
    +-----------+-----------+-----------+-----------+-----------+-----------+-----------+-----------+-----------+

Options
-------

The :class:`~benker.parsers.formex.FormexParser` parser accept the following options:

-   *formex_ns* namespace to use for Formex elements and attributes.
    Usually, a Formex document has no namespace, but in some case, you can have "http://opoce".

    For instance, if you have :

    .. literalinclude:: parsers.formex.sample2.xml
       :language: xml
       :encoding: utf-8

    To parse this XML document, you can create a parser using the *formex_ns* option:

    .. doctest:: parsers__formex

        >>> parser = FormexParser(builder, formex_ns="http://opoce")
        >>> tree = etree.parse("docs/tutorials/parsers.formex.sample2.xml")
        >>> fmx_table = tree.getroot()
        >>> table = parser.parse_table(fmx_table)
        >>> print(table)
        +-----------+-----------+
        |  Région   |    Vin    |
        +-----------+-----------+
        |  Alsace   | Gewurztra |
        +-----------+-----------+
        | Beaujolai | Brouilly  |
        +-----------+-----------+

-   *cals_ns* namespace to use for CALS-like elements and attributes.
    For the purpose of typesetting enhancement, a Formex document may contains CALS-like elements and attributes.
    This elements and attributes may use a different namespace.
    In order to parse them, you can use the *cals_ns* options.

    For instance, if you have :

    .. literalinclude:: parsers.formex.sample3.xml
       :language: xml
       :encoding: utf-8

    To parse this XML document, you can create a parser using the *cals_ns* option:

    .. doctest:: parsers__formex

        >>> parser = FormexParser(builder, cals_ns="http://my.cals.ns")
        >>> tree = etree.parse("docs/tutorials/parsers.formex.sample3.xml")
        >>> fmx_table = tree.getroot()
        >>> table = parser.parse_table(fmx_table)
        >>> print(table)
        +-----------+-----------+
        | Header 1  | Header 2  |
        +-----------+-----------+
        |  Cell A1  |  Cell B1  |
        +-----------------------+
        | Cell A2-B             |
        +-----------+-----------+
        | Cell A3-A |  Cell B3  |
        |           +-----------+
        |           |  Cell B4  |
        +-----------+-----------+


Supported values
----------------

The :class:`~benker.parsers.formex.FormexParser` parser can handle the following values:
:download:`Formex styles </_static/parsers.formex.styles.ods>`.
