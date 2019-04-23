.. Benker documentation master file, created by
   sphinx-quickstart on Thu Nov  8 17:46:28 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Benker's documentation |version|
================================

The Benker library can be used to convert tables from one format to another.

Yes, it only converts the tables, not the whole document, but it tries to do it well. The document itself
is not changed, and the paragraphs inside the cells, neither. It’s your responsibility to do this part
of the work.

.. image:: /_static/general-conversion-process.png
   :align: center
   :scale: 60 %
   :alt: General conversion process


Available formats
-----------------

The Benker library works on XML documents. Currently, it can handle:

.. list-table::
   :widths: 80 20
   :align: center
   :class: border-none vertical-align-top

   * - ✱ :abbr:`OOXML (Office Open XML)` is an XML-based format for office documents, including word processing
       documents, spreadsheets, presentations, as well as charts, diagrams, shapes, and other graphical material.
       This is the XML format used by Microsoft Word documents: ``*.docx``.

       - Officiel web site: http://officeopenxml.com/.

       - Wikipedia page: https://en.wikipedia.org/wiki/Office_Open_XML.

     - .. image:: /_static/logo-ooxml.png

   * - ✱ :abbr:`CALS (Continuous Acquisition and Life-cycle Support)` table model is a standard for representing tables
       in SGML/XML. Developed as part of the CALS Department of Defence initiative. The DTD of the CALS table model
       is available in the :abbr:`OASIS (Organization for the Advancement of Structured Information Standards)`
       web site.

       - Specification on OASIS web site: https://www.oasis-open.org/specs/tablemodels.php

       - Wikipedia page: https://en.wikipedia.org/wiki/CALS_Table_Model

     - .. image:: /_static/logo-oasis.png

   * - ✱ :abbr:`Formex (Formalized Exchange of Electronic Publications)` describes the format for the exchange
       of data between the Publication Office and its contractors. In particular, it defines the logical markup
       for documents which are published in the different series of the Official Journal of the European Union.
       Formex v4 is based on the international standard XML.

       - Official web site: http://formex.publications.europa.eu/

     - .. image:: /_static/logo-publications-office.png


Conversion stages
-----------------

To convert a document, Benker uses several stages:

#.  Parse the source document and construct a nodes tree,

#.  Search for table elements and construct the table objects,

#.  Build the target nodes tree by replacing table nodes,

#.  Serialise the target document.

.. image:: /_static/general-sequence-diagram.png
   :align: center
   :alt: General sequence diagram


Converters: Parsers + Builders
------------------------------

The decoupling between parsing, building and final serialization allows a simplified and modular implementation.
This decoupling also allows to multiply the combinations: it is easy to change a builder to another one,
and to develop its own parser…

The advantage of this approach is that we avoid having a specific document conversion for each format pair (input, output).
Instead, you can build a converter by choosing a parser and a builder, as you assemble the pieces of a puzzle.

.. image:: /_static/converter-puzzle.png
   :align: center
   :scale: 40 %
   :alt: Converter = Parser + Builder

The following table show you the available converters which groups parser and builders by pairs.

.. list-table:: **Available converters**
   :align: center
   :widths: 25 25 25 25 25
   :class: text-align-center vertical-align-middle

   * - ╲
     - .. image:: /_static/puzzle-ooxml-builder-40.png
          :scale: 60%
     - .. image:: /_static/puzzle-html-builder-40.png
          :scale: 60%
     - .. image:: /_static/puzzle-cals-builder-40.png
          :scale: 60%
     - .. image:: /_static/puzzle-formex4-builder-40.png
          :scale: 60%

   * - .. image:: /_static/puzzle-ooxml-parser-40.png
          :scale: 60%
     - –
     - *(unavailable)*
     - :func:`~benker.converters.ooxml2cals.convert_ooxml2cals`
     - :func:`~benker.converters.ooxml2formex4.convert_ooxml2formex4`

   * - .. image:: /_static/puzzle-html-parser-40.png
          :scale: 60%
     - *(unavailable)*
     - –
     - *(unavailable)*
     - *(unavailable)*

   * - .. image:: /_static/puzzle-cals-parser-40.png
          :scale: 60%
     - *(unavailable)*
     - *(unavailable)*
     - –
     - *(unavailable)*

   * - .. image:: /_static/puzzle-formex4-parser-40.png
          :scale: 60%
     - *(unavailable)*
     - *(unavailable)*
     - *(unavailable)*
     - –


You can create your own converter by inheriting the available base classes:

.. image:: /_static/general-class-diagram.png
   :align: center
   :scale: 60 %
   :alt: General class diagram (BaseConverter, BaseParser and BaseBuilder)

*   :class:`~benker.converters.base_converter.BaseConverter`:
    inherit this class to create your own converter.
    Set your own parser class to the *parser_cls* class attribute,
    and your own builder class to the *builder_cls* class attribute.

*   :class:`~benker.parsers.base_parser.BaseParser`:
    inherit this class to create your own parser.
    The method :meth:`~benker.parsers.base_parser.BaseParser.transform_tables`
    is an abstract method, so you need to implement it in your subclass: it must call
    the method :meth:`~benker.builders.base_builder.BaseBuilder.generate_table_tree`
    each time a table node is found and converted to a :class:`~benker.table.Table` object.

*   :class:`~benker.builders.base_builder.BaseBuilder`:
    inherit this class to create your own builder.
    The method :meth:`~benker.builders.base_builder.BaseBuilder.generate_table_tree`
    is an abstract method, so you need to implement it in your subclass: it must convert
    the :class:`~benker.table.Table` object into a target XML node (the resulting table format).
    You can also implement the method :meth:`~benker.builders.base_builder.BaseBuilder.finalize_tree`
    to do any post-processing to the resulting XML tree.

.. hint:: Contribution is welcome!


Usage
-----

For example, to convert the tables of a ``.docx`` document to Formex4 format, you can process as follow:

.. code-block:: python

    import os
    import zipfile

    from benker.converters.ooxml2formex4 import convert_ooxml2formex4

    # - Unzip the ``.docx`` in a temporary directory
    src_zip = "/path/to/demo.docx"
    tmp_dir = "/path/to/tmp/dir/"
    with zipfile.ZipFile(src_zip) as zf:
        zf.extractall(tmp_dir)

    # - Source paths
    src_xml = os.path.join(tmp_dir, "word/document.xml")
    styles_xml = os.path.join(tmp_dir, "word/styles.xml")

    # - Destination path
    dst_xml = "/path/to/demo.xml"

    # - Create some options and convert tables
    options = {
        'encoding': 'utf-8',
        'styles_path': styles_xml,
    }
    convert_ooxml2formex4(src_xml, dst_xml, **options)

This code produces a table like that:

.. code-block:: xml

   <TBL COLS="7" NO.SEQ="0001">
     <CORPUS>
       <ROW>
         <CELL COL="1" ROWSPAN="2">
           <w:p w:rsidR="00EF2ECA" w:rsidRDefault="00EF2ECA"><w:r><w:t>A</w:t></w:r></w:p>
         </CELL>
         <CELL COL="2" COLSPAN="2">
           <w:p w:rsidR="00EF2ECA" w:rsidRDefault="00EF2ECA"><w:r><w:t>B</w:t></w:r></w:p>
         </CELL>
         <CELL COL="4">
           <IE/>
         </CELL>
         <CELL COL="5">
           <IE/>
         </CELL>
         <CELL COL="6">
           <IE/>
         </CELL>
         <CELL COL="7">
           <IE/>
         </CELL>
       </ROW>
       <ROW>
         ...
       </ROW>
     </CORPUS>
   </TBL>

The content of the cells still contains OOXML fragments.
It's your own responsibility to convert them to the target format.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   readme.rst
   tutorials/index.rst
   api/benker.rst
   changelog.rst

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
