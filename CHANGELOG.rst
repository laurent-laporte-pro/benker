=========
Changelog
=========

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_
and this project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

v0.5.2 (unreleased)
===================

Bug fix release

Fixed
-----

* Documentation: improve API documentation for CALS table builder.

* Change in the Formex/CALS builders and parsers:
  Add support for the ``@cals:cellstyle`` attribute (extension).
  This attribute is required for two-way conversion of Formex tables to CALS and vice versa.
  If the ``CELL/@TYPE`` and the ``ROW/@TYPE`` are different, we add a specific "cellstyle" style.
  This style will keep the ``CELL/@TYPE`` value.

* Fix in ``calstblx.xsd``: change the definition of ``tgroup``: ``tfoot`` may be placed after ``tbody`` (extension).


v0.5.1 (2019-11-12)
===================

Bug fix release

Changed
-------

Add the :func:`~benker.units.parse_width` function used to parse a width and return the value and its unit.


Fixed
-----

* Documentation: add missing link to ``convert_cals2formex`` in the main page.

* Fix `#4 <https://github.com/laurent-laporte-pro/benker/issues/4>`_: Remove superfluous attributes in cals2formex.

  Change in the :class:`~benker.builders.formex.FormexBuilder` class:
  Add the :meth:`~benker.builders.formex.FormexBuilder.drop_superfluous_attrs` method:
  drop superfluous CALS-like attributes at the end of the Formex building.

* Fix `#5 <https://github.com/laurent-laporte-pro/benker/issues/5>`_: The title generation should be optional.

  Change in the :class:`~benker.builders.formex4.Formex4Builder` class:
  Add the *detect_titles* option: if this option is enable, a title will be generated
  if the first row contains an unique cell with centered text.
  The *detect_titles* options is disable by default.

* Change in the :class:`~benker.builders.formex4.Formex4Builder` class:
  Allow empty strings for *cals_ns* and *cals_prefix* options.

* Fix `#6 <https://github.com/laurent-laporte-pro/benker/issues/6>`_: Formex 2 Cals conversion: missing ``entry/@valign``.

  Change in the :class:`~benker.parsers.formex.FormexParser` class:
  The "vertical-align" style is built from the ``@cals:valign`` attribute.

  Change in the :class:`~benker.parsers.cals.CalsParser` class:
  The "vertical-align" style is built from the ``@cals:valign`` attribute.

  Change in the :class:`~benker.builders.formex.FormexBuilder` class:
  The ``@cals:valign`` attribute is built from the "vertical-align" style.

  Change in the :class:`~benker.builders.cals.CalsBuilder` class:
  The ``@cals:valign`` attribute is built from the "vertical-align" style.

* Fix `#7 <https://github.com/laurent-laporte-pro/benker/issues/7>`_: Formex 2 Cals conversion: missing ``table/@width``.

  Change in the :class:`~benker.builders.cals.CalsBuilder` class:
  Add support for the ``@width`` attribute (table width).

  Change in the :class:`~benker.builders.formex.FormexBuilder` class:
  Add support for the ``@width`` CALS-like attribute (table width).

* Minor change in the :class:`~benker.parsers.ooxml.OoxmlParser` class:
  XML indentation between cell paragraphs is ignored.

* Fix `#9 <https://github.com/laurent-laporte-pro/benker/issues/9>`_: Cals 2 Formex conversion:
  Text and PIs lost in entries.

  Add the :meth:`~benker.builders.base_builder.BaseBuilder.append_cell_elements` method:
  Append XML elements, PIs or texts to a cell element.

  Change in the :class:`~benker.builders.cals.CalsBuilder` and :class:`~benker.builders.formex.FormexBuilder` classes:
  Preserve processing instruction in cell content.

* Fix `#10 <https://github.com/laurent-laporte-pro/benker/issues/10>`_: Formex 2 Cals conversion: ``GR.NOTES`` should be preserved.

  Change in :class:`~benker.parsers.formex.FormexParser` class:
  ``GR.NOTES`` elements can be embedded if the *embed_gr_notes* options is ``True``.

  Change in the :class:`~benker.builders.formex.FormexBuilder` class:
  During ``GR.NOTES`` extraction, existing ``GR.NOTES`` are moved before the ``CORPUS``
  (or created if missing).

  Change in the :func:`~benker.converters.formex2cals.convert_formex2cals` function:
  Add the *embed_gr_notes* options to allow ``GR.NOTES`` element embedding.


* Fix `#11 <https://github.com/laurent-laporte-pro/benker/issues/11>`_: Cals 2 Formex conversion: missing ``CORPUS/@width``.

  Change in the :class:`~benker.parsers.cals.CalsParser` class:
  Add the ``width_unit`` option, and add support for the ``@cals:width`` attribute (table width).

* Fix `#12 <https://github.com/laurent-laporte-pro/benker/issues/12>`_: Cals 2 Formex conversion: missing ``colspec`` attributes.

  Change in the :class:`~benker.builders.formex.FormexBuilder` class:
  Add support for CALS-like attributes: ``@colnum``, ``@align``, ``@colsep``, and ``@rowsep``
  in the ``colspec`` element.

  Change in the :class:`~benker.builders.cals.CalsBuilder` class:
  The ``@colsep`` and ``@rowsep`` attributes are generated.


Other
-----

* Change link to the Formex documentation to "https://op.europa.eu/en/web/eu-vocabularies/formex".

* Change Tox & AppVeyor configuration to use lxml v4.3.3 on Windows (for Python 3.4),
  because lxml v4.3.5 is not available for this platform.


v0.5.0 (2019-09-25)
===================

Minor release

Changed
-------

* Refactoring (rename "Formex4" to "Formex"):

  - the module ``benker/builders/formex4.py`` is renamed ``benker/builders/formex.py``,
  - the module ``benker/converters/ooxml2formex4.py`` is renamed ``benker/converters/ooxml2formex.py``,
  - the module ``benker/parsers/formex4.py`` is renamed ``benker/parsers/formex.py``,
  - the class ``Formex4Builder`` is renamed ``FormexBuilder``,
  - the class ``Ooxml2Formex4Converter`` is renamed ``Ooxml2FormexConverter``,
  - the function ``convert_ooxml2formex4`` is renamed ``convert_ooxml2formex``,
  - the class ``Formex4Parser`` is renamed ``FormexParser``,

* Change in the class :class:`~benker.table.Table`:
  add the method :meth:`~benker.table.Table.fill_missing` to fill the missing cells in a table.

* Change in the class :class:`~benker.builders.cals.CalsBuilder`:
  Add support for the ``@cals:rowstyle`` attribute (extension).
  The ``@colnum`` and ``@align`` attributes are generated for the ``<colspec>`` element.
  The new options *cals_ns* and *cals_prefix* allow the used of namespaces in CALS.
  The option *tgroup_sorting* can be used to sort the ``thead``, ``tbody`` and ``tfoot`` elements.

* Change in the method :class:`~benker.parsers.base_parser.BaseParser.parse_file`:
  Always generate the XML declaration in the destination file.

Added
-----

* Change in the converter: :func:`~benker.converters.ooxml2formex.convert_ooxml2formex`:
  Add the option *use_cals* (and related options: *cals_ns*, *cals_prefix* and *width_unit*):
  This options is used to generate additional CALS-like elements and attributes
  to simplify the layout of Formex document in typesetting systems.

* Add support for the Table/Cell shading in the OOXML parser.

* Add support for ``bgcolor`` (Table/Cell background color) in the CALS builder.

* Add support for ``bgcolor`` (Table/Cell background color) in the Formex 4 builder
  (only with the *use_cals* option).

* New parser: :class:`~benker.parsers.cals.CalsParser`: CALS tables parser.


Fixed
-----

* Change in the builder :class:`~benker.builders.cals.CalsBuilder`:
  the possible values for row/cell *nature* is "header", "body" and "footer"
  (instead of "head", "body", "foot").

* Fix in the class :class:`~benker.parsers.ooxml.OoxmlParser`: rows with missing cells are filled
  with empty cells of the same nature as the row.

Other
-----

* Fix an issue with the AppVeyor build: upgrade setuptools version in ``appveyor.yml``,
  change the Tox configuration: set ``py27,py34,py35: pip >= 9.0.3, < 19.2``.

* Change the project‘s slogan: “Easily convert your CALS, HTML, Formex 4, Office Open XML (docx)
  tables from one format to another.”

* Change Tox configuration file to test the library with lxml v4.3 on Python 3.4
  (support for Python 3.4 was removed in `lxml v4.4 <https://lxml.de/4.4/changes-4.4.0.html>`_).

* Change Tox configuration file to test the library on Python 3.8.

* Change the Travis CI configuration to build on Python 3.7 and 3.8-dev.


v0.4.3 (unreleased)
===================

Bug fix release

Fixed
-----

* Fix `#5 <https://github.com/laurent-laporte-pro/benker/issues/5>`_: The title generation should be optional.

  Change in the :class:`~benker.builders.formex4.Formex4Builder` class:
  Add the *detect_titles* option: if this option is enable, a title will be generated
  if the first row contains an unique cell with centered text.
  The *detect_titles* options is disable by default.


v0.4.2 (2019-06-06)
===================

Bug fix release

Fixed
-----

* Fix `#1 <https://github.com/laurent-laporte-pro/benker/issues/1>`_: Cell nature should inherit row nature by default.

  Change in the class :class:`~benker.styled.Styled`:
  The default value of the *nature* parameter is ``None`` (instead of "body").

  Change in the methods :meth:`~benker.table.RowView.insert_cell` and :meth:`~benker.table.ColView.insert_cell`
  The *nature* of a cell is inherited from its parent's row (or column).

Other
-----

* Change the requirements for Sphinx: add 'requests[security]' for Python 2.7.

* Fix an issue with the AppVeyor build: change the Tox configuration: set ``py27,py34,py35: pip >= 9.0.3``.


v0.4.1 (2019-04-24)
===================

Bug fix release

Fixed
-----

* Change in the parser :class:`~benker.parsers.ooxml.OoxmlParser`:
  fix the 'x-sect-cols' value extraction when the ``w:sectPr`` is missing (use "1" by default).

* Fix the Formex 4 builder :class:`~benker.builders.formex.FormexBuilder`:
  Generate a ``<IE/>`` element if the cell content (the string representation) is empty.


v0.4.0 (2019-04-23)
===================

Feature release

Added
-----

* New converter: :func:`~benker.converters.ooxml2formex.convert_ooxml2formex`:
  Convert Office Open XML (OOXML) tables to Formex 4 tables.

* New builder: :class:`~benker.builders.formex.FormexBuilder`:
  Formex 4 builder used to convert tables into ``TBL`` elements.

* Change in the parser :class:`~benker.parsers.ooxml.OoxmlParser`:

  - The section width and height are now stored in the 'x-sect-size' table style (units in 'pt').

* Change in the builder :class:`~benker.builders.base_builder.BaseBuilder`:
  Add the method :meth:`~benker.builders.base_builder.BaseBuilder.finalize_tree`:
  Give the opportunity to finalize the resulting tree structure.


v0.3.0 (2019-02-16)
===================

Feature release

Added
-----

* Change in the parser :class:`~benker.parsers.ooxml.OoxmlParser`:

  - Parse cell ``w:tcPr/w:vAlign`` values.

  - Parse paragraph alignments to calculate cell horizontal alignments.

  - Parse cell ``w:tcPr/w:tcBorders`` values to extract border styles.

* Change in the builder :class:`benker.builders.cals.CalsBuilder`:

  - Generate ``entry/@valign`` attributes.

  - Generate ``entry/@align`` attributes.

  - Generate ``entry/@colsep`` and ``entry/@rowsep`` attributes.

Changed
-------

* Change in the parser :class:`~benker.parsers.ooxml.OoxmlParser`:

  - Add more supported `border styles <http://www.datypic.com/sc/ooxml/t-w_ST_Border.html>`_


v0.2.2 (2018-12-15)
===================

Bug fix release

Added
-----

* Add a Python alternative to :class:`lxml.etree.iterwalk` if using lxml < 4.2.1.
  See `lxml changelog v4.2.1 <https://lxml.de/4.2/changes-4.2.1.html>`_.

Fixed
-----

* Fix the implementation of :meth:`~benker.parsers.ooxml.OoxmlParser.parse_table`:
  use a new implementation of :class:`lxml.etree.iterwalk` if using lxml < 4.2.1.

Other
-----

* Change Tox configuration file to test the library with lxml v3 and v4.

* Add a changelog in the documentation.


v0.2.1 (2018-11-27)
===================

Fixed
-----

* Fix Coverage configuration file.

* Fix and improve configuration for Tox.

* Fix docstring in :mod:`~benker.converters.ooxml2cals`.

* Fix calculation of the ``@frame`` attribute in the method :meth:`benker.builders.cals.CalsBuilder.build_table`.

Other
-----

* Change link to PyPi project to "https://pypi.org/project/Benker/".

* Add the README to the documentation.

* Add configuration files for TravisCI and AppVeyor.


v0.2.0 (2018-11-26)
===================

Changed
-------

* Update project configuration

* Add missing ``__init__.py`` file in ``tests`` directory: it is required for test modules import.

Fixed
-----

* Fix unit tests (Python 2.7).

* Fix flakes8 problems.

* Fix implementation of the :class:`~benker.grid.Grid` class for Python 2.7 (remove annotation). And minor fixes.

* Remove pipenv configuration files.

* Fix project configuration.


v0.1.0 (2018-11-26)
===================

* First version of Benker.
