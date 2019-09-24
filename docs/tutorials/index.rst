Tutorials
=========

This section presents the different tutorials available to discover and learn how to use Benker.
This library has high-level conversion functions to convert tables from one format to another.
All functions have the same API, it's easier for everyone.

The following tutorials will give you sample files to convert and the expected results.
Of course, you will have the opportunity to choose your conversion options according to your needs:

.. toctree::
   :maxdepth: 1
   :titlesonly:
   :caption: Converters:

   converters.ooxml2formex
   converters.ooxml2cals
   converters.formex2cals

.. note:: future converters are coming.

All the converters available in the benker library use parser/builder pairs.
There is one parser for each XML document type to read and one builder for each XML document type to write.
For example, you have the parser OOXML which will allow you to analyze the tables contained in Word documents
(of type ``.docx``); and you can choose the Formex builder to generate valid Formex 4 tables.

The following tutorials will give you some use cases for parsers and builders.
You could immerse yourself in the classes usage and available options.

.. toctree::
   :maxdepth: 1
   :titlesonly:
   :caption: Parsers:

   parsers.ooxml
   parsers.formex
   parsers.cals

.. toctree::
   :maxdepth: 1
   :titlesonly:
   :caption: Builders:

   builders.formex
   builders.cals

.. note:: future parsers and builders are coming.

.. warning::

    here, we are talking about tables parsers and not documents parsers:
    only tables are analyzed and converted into an object structure in memory. The rest of the document is not touched (only namespaces).

The Benker Library also has low-level functions in core modules.
These core modules are the essential building blocks for having in memory table structures.
A set of tutorials is also available for these modules.

.. toctree::
   :maxdepth: 1
   :titlesonly:
   :caption: Core modules:

   size.rst
   coord.rst
   box.rst
   styled.rst
   cell.rst
   grid.rst
   table.rst
