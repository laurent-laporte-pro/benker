=========
Changelog
=========

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_
and this project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.


v0.3.0 (unreleased)
===================

Feature release

Added
-----

* Change in the parser :class:`~benker.parsers.ooxml.OoxmlParser`:

  - Parse cell ``w:tcPr/w:vAlign`` values.

  - Parse paragraph alignments to calculate cell horizontal alignments.

* Change in the builder :class:`benker.builders.cals.CalsBuilder`:

  - Generate ``entry/@valign`` attributes.

  - Generate ``entry/@align`` attributes.


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

* Fix docstring in :mod:`~benker.ooxml2cals`.

* Fix calculation of the ``@frame`` attribute in the function :func:`benker.builders.cals._get_frame_attr`.

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
