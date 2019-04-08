.. _usage:

Usage
=====

The Benker library can be used to convert tables from one format to another.

To convert a document, Benker uses several stages:

-   First, it parses the document, searching for the table elements (XML elements),
-   For each table element, it build a intermediate object of type :class:`~benker.table.Tbale`,
-   Then, it converts the intermediate object into the destination XML element.

The decoupling between parsing, building and final conversion allows a simplified and modular implementation.
This decoupling also allows to multiply the combinations: it is easy to change a builder to another one.

.. list-table:: **Available parsers/builders**
   :header-rows: 1

   * - \
     - :abbr:`OOXML (Office Open XML)`
     - :abbr:`CALS (Continuous Acquisition and Life-cycle Support)`
     - :abbr:`Formex (Formalized Exchange of Electronic Publications)`
   * - **OOXML**
     - –
     - :func:`~benker.converters.ooxml2cals.convert_ooxml2cals`
     - :func:`~benker.converters.ooxml2formex4.convert_ooxml2formex4`
   * - **CALS**
     -
     - –
     -
   * - **Formex4**
     -
     -
     - –

Example: to convert the tables of a ``.docx`` document to Formex4 format, you can process as follow:

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
        'styles_path': str(styles_xml),
    }
    convert_ooxml2formex4(str(src_xml), str(dst_xml), **options)

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

