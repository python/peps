..
   Author: Adam Turner


Building PEPs Locally
=====================

Whilst editing a PEP, it is useful to review the rendered output locally.
This can also be used to check that the PEP is valid reStructuredText before
submission to the PEP editors.

The rest of this document assumes you are working from a local clone of the
`PEPs repository <https://github.com/python/peps>`__, with Python 3.9 or later
installed.


Render PEPs locally
-------------------

1. Create a virtual environment and install requirements

   .. code-block:: console

      $ python -m venv venv
      $ . venv/bin/activate
      (venv) $ python -m pip install --upgrade pip
      (venv) $ python -m pip install -r requirements.txt

2. **(Optional)** Delete prior build files.
   Generally only needed when making changes to the rendering system itself.

   .. code-block:: console

      $ rm -rf build

3. Run the build script:

   .. code-block:: console

      (venv) $ make sphinx

   If you don't have access to ``make``, run:

   .. code-block:: ps1con

      (venv) PS> python build.py -j 8

   .. note::

      There may be a series of warnings about unreferenced citations or labels.
      Whilst these are valid warnings, they do not impact the build process.

4. Navigate to the ``build`` directory of your PEPs repo to find the HTML pages.
   PEP 0 provides a formatted index, and may be a useful reference.


``build.py`` tools
------------------

Several additional tools can be run through ``build.py``, or the Makefile.


Check links
'''''''''''

Check the validity of links within PEP sources (runs the `Sphinx linkchecker
<https://www.sphinx-doc.org/en/master/usage/builders/index.html#sphinx.builders.linkcheck.CheckExternalLinksBuilder>`__).

.. code-block:: console

    (venv) $ python build.py --check-links
    (venv) $ make check-links


Stricter rendering
''''''''''''''''''

Run in `nit-picky <https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-nitpicky>`__
mode.
This generates warnings for all missing references.

.. code-block:: console

    (venv) $ python build.py --nitpicky

Fail the build on any warning.
As of January 2022, there are around 250 warnings when building the PEPs.

.. code-block:: console

    (venv) $ python build.py --fail-on-warning
    (venv) $ make fail-warning


All arguments to ``build.py``
-----------------------------

For details on options to ``build.py``, run:

.. code-block:: console

    (venv) $ python build.py --help
