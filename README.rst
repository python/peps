Python Enhancement Proposals
============================

.. image:: https://github.com/python/peps/actions/workflows/render.yml/badge.svg
    :target: https://github.com/python/peps/actions

The PEPs in this repo are published automatically on the web at
https://peps.python.org/. To learn more about the purpose of PEPs and how to go
about writing one, please start reading at :pep:`1`. Note that the PEP Index
(:pep:`0`) is automatically generated based on the metadata headers in other PEPs.


Contributing to PEPs
====================

See the `Contributing Guidelines <./CONTRIBUTING.rst>`_.


Checking PEP formatting and rendering
=====================================

Please don't commit changes with reStructuredText syntax errors that cause PEP
generation to fail, or result in major rendering defects relative to what you
intend.


Browse the ReadTheDocs preview
------------------------------

For every PR, we automatically create a preview of the rendered PEPs using
`ReadTheDocs <https://readthedocs.org/>`_.
You can find it in the merge box at the bottom of the PR page:

1. Click "Show all checks" to expand the checks section
2. Find the line for ``docs/readthedocs.org:pep-previews``
3. Click on "Details" to the right


Render PEPs locally
-------------------

See the `build documentation <./docs/build.rst>`__ for full
instructions on how to render PEPs locally.
In summary, run the following in a fresh, activated virtual environment:

.. code-block:: bash

    # Install requirements
    python -m pip install -U -r requirements.txt

    # Render the PEPs
    make render

    # Or, if you don't have 'make':
    python build.py

The output HTML is found under the ``build`` directory.


Check and lint PEPs
-------------------

You can check for and fix common linting and spelling issues,
either on-demand or automatically as you commit, with our pre-commit suite.
See the `Contributing Guide <./CONTRIBUTING.rst>`_ for details.
