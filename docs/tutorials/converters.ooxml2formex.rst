.. _benker__converters__ooxml__formex:

.. testsetup:: converter__ooxml__formex

    import shutil
    import tempfile
    tmp_dir = tempfile.mkdtemp(prefix="benker.docs.tutorials.converters.ooxml2formex_")

.. testcleanup:: converter__ooxml__formex

    shutil.rmtree(tmp_dir)

OOXML to Formex 4 converter
===========================

Description
-----------

.. _Office Open XML File Formats: https://www.ecma-international.org/publications/standards/Ecma-376.htm
.. _Formex 4 format: https://publications.europa.eu/en/web/eu-vocabularies/formex


The :func:`~benker.converters.ooxml2formex.convert_ooxml2formex` converter is a function designed to convert tables from an Office Open XML (OOXML) document (which respects the schema defined in `Office Open XML File Formats`_) in the `Formex 4 format`_.

The conversion is done in the source XML document by replacing the tables of the OOXML format with those transformed in the Formex format.
In other words, the general structure of the source XML document is retained except for tables.

The :class:`~benker.converters.ooxml2formex.Ooxml2FormexConverter` converter is composed of:

*   a :class:`~benker.parsers.ooxml.OoxmlParser` parser that allows you to parse tables in OOXML format,

    The tutorial :ref:`benker__parsers__ooxml` describes the usage of this parser and gives some examples.

*   a :class:`~benker.builders.formex.FormexBuilder` builder that allows you to build tables in the Formex format.

    The tutorial :ref:`benker__builders__formex` describes the usage of this builder and gives some examples.

Conversion options
------------------

The tables parsing and building can be parameterized using the options described below:

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

Examples of conversions
-----------------------

Converting a ``.docx`` document
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can use the :func:`~benker.converters.ooxml2formex.convert_ooxml2formex` converter
to convert a Word document, for instance, we have the following annex:

.. image:: /_static/converters.ooxml2formex.sample1.jpeg

If you want to convert a ``.docx`` file, you need first to decompress it in a temporary directory
in order to access the "word/document.xml" and "word/styles.xml" stored in the ``.docx`` package.

To decompress the ``.docx`` package and convert the tables, you can do:

.. doctest:: converter__ooxml__formex

    >>> import os
    >>> import zipfile

    >>> from benker.converters.ooxml2formex import convert_ooxml2formex

    >>> src_zip = "docs/_static/converters.ooxml2formex.sample1.docx"
    >>> with zipfile.ZipFile(src_zip) as zf:
    ...     zf.extractall(tmp_dir)

    >>> src_xml = os.path.join(tmp_dir, "word/document.xml")
    >>> styles_xml = os.path.join(tmp_dir, "word/styles.xml")

    >>> dst_xml = os.path.join(tmp_dir, "converters.ooxml2formex.sample1.xml")
    >>> options = {
    ...     'encoding': 'utf-8',
    ...     'styles_path': styles_xml,
    ... }
    >>> convert_ooxml2formex(src_xml, dst_xml, **options)

The result is the "word/document.xml" document, but with tables replaced by the Formex ``TBL`` elements.

Here is a sample of the result XML:

.. literalinclude:: /_static/converters.ooxml2formex.sample1.xml
   :language: xml
   :encoding: utf-8
   :lines: 1-84
   :emphasize-lines: 29-

Using CALS-like attributes and elements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Formex table format is good to structure tables. The logical structure is similar to the one used for HTML tables
but without CSS.

Some difficulties appears when you want to do the layout of Formex tables in typesetting systems:
Formex tables doesn't have much layout information:

*   no borders,
*   no horizontal of vertical alignment of the text,
*   no background color,
*   no indication of the column width,
*   etc.

To solve that, it is possible to generate CALS-like attributes and elements in the Formex.
Of course, we can use a namespace and a namespace prefix for the CALS attributes and elements.

To convert the tables using CALS, you can do:

.. doctest:: converter__ooxml__formex

    >>> dst_xml = os.path.join(tmp_dir, "converters.ooxml2formex.sample2.xml")
    >>> options = {
    ...     'encoding': 'utf-8',
    ...     'styles_path': styles_xml,
    ...     'use_cals': True,
    ...     'cals_ns': "http://cals",
    ...     'cals_prefix': "cals",
    ... }
    >>> convert_ooxml2formex(src_xml, dst_xml, **options)

The result is the "word/document.xml" document, but with tables replaced by the Formex ``TBL`` elements.

Here is a sample of the result XML:

.. literalinclude:: /_static/converters.ooxml2formex.sample2.xml
   :language: xml
   :encoding: utf-8
   :lines: 9-55

In the result, we can notice:

*   the presence of the namespace ``xmlns:cals="http://cals"``.
*   the additional attributes, like ``cals:frame="none"``, ``cals:colsep="0"``, ``cals:rowsep="0"``...
*   the additional ``colspec`` elements: ``<cals:colspec cals:colname="c1" cals:colwidth="24.04mm"/>``.

This kind of information is will be preserved if you use a Formex to CALS conversion
(see the :ref:`benker__converters__formex__cals` tutorial).
