Benker
======

.. _virtualenv: https://virtualenv.pypa.io/en/latest/
.. _lxml: https://lxml.de/
.. _CALS: https://en.wikipedia.org/wiki/CALS_Table_Model
.. _MIT: https://opensource.org/licenses/mit-license.php

.. image:: https://img.shields.io/pypi/v/Benker.svg
    :target: https://pypi.org/project/Benker/
    :alt: Latest PyPI version

.. image:: https://api.travis-ci.com/laurent-laporte-pro/benker.svg?branch=master
   :target: https://app.travis-ci.com/laurent-laporte-pro/benker
   :alt: Latest Travis CI build status

.. image:: https://ci.appveyor.com/api/projects/status/758w8evuqo29i5dw?svg=true
   :target: https://ci.appveyor.com/project/laurent-laporte-pro/benker
   :alt: Latest AppVeyor build status

.. image:: https://img.shields.io/badge/license-MIT-blue.svg
   :target: https://raw.githubusercontent.com/laurent-laporte-pro/benker/master/LICENSE
   :alt: GitHub license

Easily convert your CALS, HTML, Formex4, Office Open XML (docx) tables from one format to another.

Overview
--------

To convert the tables of a ``.docx`` document to CALS_ format, you can process as follow:

.. code-block:: python

    import os
    import zipfile

    from benker.converters.ooxml2cals import convert_ooxml2cals

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
        'width_unit': "mm",
        'table_in_tgroup': True,
    }
    convert_ooxml2cals(src_xml, dst_xml, **options)

Installation
------------

To install this library, you can create and activate a virtualenv_, and run:

.. code-block:: bash

    pip install benker

Requirements
^^^^^^^^^^^^

This library uses lxml_ library and is tested with the versions 3.8 and 4.*x*.

The following table shows the compatibility between different combinations of Python and lxml versions:

+-----------+------+------+------+------+------+------+------+------+
| Py ╲ lxml | 3.8  | 4.0  | 4.1  | 4.2  | 4.3  | 4.4  | 4.5  | 4.6  |
+===========+======+======+======+======+======+======+======+======+
| **2.7**   |  ✔️  |  ✔️  |  ✔️  |  ✔️  |  ✔️  |  ✔️  |  ✔️  |  ✔️  |
+-----------+------+------+------+------+------+------+------+------+
| **3.4**   |  ✔️! | ✔️!  | ✔️!  | ✔️!  | ✔️!  |  ✖️  |  ✖️  |  ✖️  |
+-----------+------+------+------+------+------+------+------+------+
| **3.5**   |  ✔️  |  ✔️  |  ✔️  |  ✔️  |  ✔️  |  ✔️  |  ✔️  |  ✔️  |
+-----------+------+------+------+------+------+------+------+------+
| **3.6**   |  ✔️  |  ✔️  |  ✔️  |  ✔️  |  ✔️  |  ✔️  |  ✔️  |  ✔️  |
+-----------+------+------+------+------+------+------+------+------+
| **3.7**   |  ✖️  |  ✖️  |  ✔️  |  ✔️  |  ✔️  |  ✔️  |  ✔️  |  ✔️  |
+-----------+------+------+------+------+------+------+------+------+
| **3.8**   |  ✖️  |  ✖️  |  ✖️  |  ✖️  |  ✔️  |  ✔️  |  ✔️  |  ✔️  |
+-----------+------+------+------+------+------+------+------+------+
| **3.9**   |  ✖️  |  ✖️  |  ✖️  |  ✖️  |  ✔️  |  ✔️  |  ✔️  |  ✔️  |
+-----------+------+------+------+------+------+------+------+------+

- ✔️ lxml is available for this version and unit tests succeed.
- ! installation succeed using "attrs < 21.1".
- ✖️ lxml is not available for this version of Python.

.. see ``envlist`` in tox.ini.

Usage in your library/application
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can use this library in your own library/application.

To do so, add this library in your ``setup.py`` in your project requirements:

.. code-block:: python

    setup(
        name="YourApp",
        install_requires=['benker'],
        ...
    )

To install the dependencies, activate your virtualenv_ and run:

.. code-block:: bash

    pip install -e .

And enjoy!

Licence
-------

This library is distributed according to the MIT_ licence.

Users have legal right to download, modify, or distribute the library.

Authors
-------

``Benker`` was written by `Laurent LAPORTE <laurent.laporte.pro@gmail.com>`_.
