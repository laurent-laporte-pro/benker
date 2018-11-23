.. This documentation can be updated with the following command:
   sphinx-apidoc -o docs/api/ . "setup.py" "test_*.py" --separate --no-toc --no-headings --module-first

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

.. toctree::
   :maxdepth: 1
   :caption: Core modules:

   benker.size
   benker.coord
   benker.box
   benker.styled
   benker.cell
   benker.grid
   benker.table
   benker.parsers
   benker.builders
   benker.converters

.. toctree::
   :maxdepth: 1
   :caption: Utilities:

   benker.alphabet
   benker.drawing
   benker.units
