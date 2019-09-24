.. _benker__parsers__cals:

CALS tables parser
==================

Description
-----------

A :class:`~benker.parsers.cals.CalsParser` is used to parse the tables (``table`` elements) of a CALS file
and generate a :class:`~benker.table.Table` instances (memory representation of a table).
The instance can then be serialize in another XML format, like HTML, Formex 4 or even CALS.

To use this class, you need to inherit the :class:`~benker.builders.base_builder.BaseBuilder` class
and create an instance of your class to used in the :class:`~benker.parsers.cals.CalsParser` parser.

Of course, for the sake of this demonstration we can used an instance
of the class :class:`~benker.builders.base_builder.BaseBuilder`, without implementing
the :meth:`~benker.builders.base_builder.BaseBuilder.generate_table_tree` method.

.. doctest:: parsers__cals

    >>> from lxml import etree
    >>> from benker.builders.base_builder import BaseBuilder
    >>> from benker.parsers.cals import CalsParser

    >>> builder = BaseBuilder()
    >>> parser = CalsParser(builder)

For exemple, you can parse the following CALS table:

.. literalinclude:: parsers.cals.sample1.xml
   :language: xml
   :encoding: utf-8

And generate a :class:`~benker.table.Table` instance:

.. doctest:: parsers__cals

    >>> tree = etree.parse("docs/tutorials/parsers.cals.sample1.xml")
    >>> cals_table = tree.getroot()
    >>> table = parser.parse_table(cals_table)
    >>> print(table)
    +-----------+-----------+-----------+
    |  Element  |    (Z)    |    (A)    |
    +-----------+-----------+-----------+
    | Hydrogen  |     1     |   1.008   |
    +-----------+-----------+-----------+
    |  Helium   |     2     |  4.0026   |
    +-----------+-----------+-----------+
    |  Lithium  |     3     |   6.94    |
    +-----------+-----------+-----------+


Options
-------

The :class:`~benker.parsers.cals.CalsParser` parser accept the following options:

-   *cals_ns* is used to specify a specific namespace used by your CALS tables.

    For instance, if you have :

    .. literalinclude:: parsers.cals.sample2.xml
       :language: xml
       :encoding: utf-8

    To parse this XML document, you can create a parser using the *cals_ns* option:

    .. doctest:: parsers__cals

        >>> parser = CalsParser(builder, cals_ns="http://my.cals.ns")
        >>> tree = etree.parse("docs/tutorials/parsers.cals.sample2.xml")
        >>> cals_table = tree.getroot()
        >>> table = parser.parse_table(cals_table)
        >>> print(table)
        +-----------+-----------+-----------+
        |           |     k     |   unit    |
        +-----------+-----------+-----------+
        |   Meter   |    km     |     m     |
        +-----------+-----------+-----------+
        |   Liter   |    KL     |     L     |
        +-----------+-----------+-----------+
        |   Gram    |    Kg     |     g     |
        +-----------+-----------+-----------+


Supported values
----------------

The :class:`~benker.parsers.cals.CalsParser` parser can handle the following values:
:download:`CALS styles </_static/parsers.cals.styles.ods>`.
