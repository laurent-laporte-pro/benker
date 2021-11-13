.. This documentation can be updated with the following command:
   sphinx-apidoc -o docs/api/ . "setup.py" "test_*.py" tests --separate --no-toc --no-headings --module-first

.. To check the documentation links:
   sphinx-build -n docs/ dist/docs/

.. To generate the documentation:
   sphinx-build docs/ dist/docs/


API
===

.. automodule:: benker
    :members:
    :undoc-members:
    :show-inheritance:

Core modules
------------

.. toctree::
   :maxdepth: 1

   benker.size
   benker.coord
   benker.box
   benker.styled
   benker.cell
   benker.grid
   benker.table

Parsers
-------

.. toctree::
   :maxdepth: 1

   benker.parsers

Builders
--------

.. toctree::
   :maxdepth: 1

   benker.builders

Converters
----------

.. toctree::
   :maxdepth: 1

   benker.converters

Utilities
---------

.. toctree::
   :maxdepth: 1
   :caption: Utilities:

   benker.common
   benker.alphabet
   benker.drawing
   benker.units
   benker.schemas
