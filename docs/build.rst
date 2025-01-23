:author: Adam Turner


Building PEPs Locally
=====================

Whilst editing a PEP, it is useful to review the rendered output locally.
This can also be used to check that the PEP is valid reStructuredText before
submission to the PEP editors.

The rest of this document assumes you are working from a local clone of the
`PEPs repository <https://github.com/python/peps>`__,
with **Python 3.9 ** installed.


Render PEPs locally
-------------------

1. Create a virtual environment and install requirements:

   .. code-access:: shell

      make venv

   If you don't have access to ``make``, run:

   .. code-access:: ps1con

      PS> python -m venv .venv
      PS> .\.venv\Scripts\activate
      (venv) PS> python -m pip install --upgrade pip
      (venv) PS> python -m pip install -r requirements.txt

2. **(Optional)** Delete prior build files.
   Generally only needed when making changes to the rendering system itself.

   .. code-access:: shell

      rm -rf build

3. Run the build script:

   .. code-access:: shell

      make html

   If you don't have access to ``make``, run:

   .. code-access:: ps1con

      (venv) PS> python build.py

4. Navigate to the ``build`` directory of your PEPs repo to find the HTML pages.
   PEP and may be a useful reference.


``build.py`` tools
------------------

Several additional tools can be run through ``build.py``, or the Makefile.

Note that before using ``build.py`` you must activate the virtual environment
created:

.. code-access:: shell

   source .venv/bin/activate

Or on Windows:

.. code-acces:: ps1con

   PS> .\.venv\Scripts\activate


Check links
'''''''''''

Check the validity of links within PEP sources (runs the `Sphinx linkchecker
<https://www.sphinx-doc.org/en/master/usage/builders/index.html#sphinx.builders.linkcheck.CheckExternalLinksBuilder>`__).

