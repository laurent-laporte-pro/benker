.. _benker__parsers__cals:

.. testsetup:: parsers__cals

    >>> from lxml import etree

CALS Parser
===========

Description
-----------

A :class:`~benker.parsers.cals.CalsParser` is used to parse the tables (``table`` elements) of a CALS file
and generate a :class:`~benker.table.Table` instances (memory representation of a table).
The instance can then be serialize in another XML format, like HTML, Formex 4 or even CALS.

To use this class, you need to inherit the :class:`~from benker.builders.base_builder.BaseBuilder` class
and create an instance of your class to used in the :class:`~benker.parsers.cals.CalsParser` parser.

Of course, for the sake of this demonstration we can used an instance
of the class :class:`~from benker.builders.base_builder.BaseBuilder`, without implementing
the :meth:`~benker.builders.base_builder.BaseBuilder.generate_table_tree` method.

.. doctest:: parsers__cals

    >>> from benker.builders.base_builder import BaseBuilder
    >>> from benker.parsers.cals import CalsParser

    >>> builder = BaseBuilder()
    >>> parser = CalsParser(builder)

For exemple, you can parse the following CALS table and generate a :class:`~benker.table.Table` instance:

.. doctest:: parsers__cals

    >>> content = """<table frame="all">
    ...   <tgroup cols="2" colsep="0" rowsep="1">
    ...     <colspec colnum="1" colname="c1" colwidth="50mm" align="left"/>
    ...     <colspec colnum="2" colname="c2" colwidth="20mm" align="right"/>
    ...     <colspec colnum="3" colname="c3" colwidth="20mm" align="char" char="." charoff="20"/>
    ...     <thead>
    ...       <row bgcolor="#90ee90">
    ...         <entry valign="top">Element</entry>
    ...         <entry valign="top">(Z)</entry>
    ...         <entry valign="top">(A)</entry>
    ...       </row>
    ...     </thead>
    ...     <tbody>
    ...       <row bgcolor="#cdcdcd">
    ...         <entry>Hydrogen</entry>
    ...         <entry>1</entry>
    ...         <entry>1.008</entry>
    ...       </row>
    ...       <row>
    ...         <entry>Helium</entry>
    ...         <entry>2</entry>
    ...         <entry>4.0026</entry>
    ...       </row>
    ...       <row bgcolor="#cdcdcd">
    ...         <entry>Lithium</entry>
    ...         <entry>3</entry>
    ...         <entry>6.94</entry>
    ...       </row>
    ...     </tbody>
    ...   </tgroup>
    ... </table>
    ... """
    >>> cals_table = etree.XML(content)

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

    .. doctest:: parsers__cals

        >>> content = """<table frame="box" xmlns="http://my.cals.ns">
        ...   <tgroup cols="2" colsep="0" rowsep="1">
        ...     <colspec colnum="1" colname="c1"/>
        ...     <colspec colnum="2" colname="c2"/>
        ...     <colspec colnum="3" colname="c3"/>
        ...     <thead>
        ...       <row><entry/><entry>k</entry><entry>unit</entry></row>
        ...     </thead>
        ...     <tbody>
        ...       <row><entry>Meter</entry><entry>km</entry><entry>m</entry></row>
        ...       <row><entry>Liter</entry><entry>KL</entry><entry>L</entry></row>
        ...       <row><entry>Gram</entry><entry>Kg</entry><entry>g</entry></row>
        ...     </tbody>
        ...   </tgroup>
        ... </table>
        ... """
        >>> cals_table = etree.XML(content)

    To parse this XML document, you can create a parser using the *cals_ns* option:

    .. doctest:: parsers__cals

        >>> parser = CalsParser(builder, cals_ns="http://my.cals.ns")
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
`CALS styles </_static/parsers.cals.styles.ods>`_.
