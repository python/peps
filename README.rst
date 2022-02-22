Python Enhancement Proposals
============================

.. image:: https://github.com/python/peps/actions/workflows/build.yml/badge.svg
    :target: https://github.com/python/peps/actions

The PEPs in this repo are published automatically on the web at
https://www.python.org/dev/peps/.  To learn more about the purpose of
PEPs and how to go about writing one, please start reading at `PEP 1
<https://www.python.org/dev/peps/pep-0001/>`_.
Note that PEP 0, the index PEP, is
automatically generated and not committed to the repo.


Contributing to PEPs
====================

See the `Contributing Guidelines <./CONTRIBUTING.rst>`_.


reStructuredText for PEPs
=========================

PEP source text should be written in reStructuredText format,
which is a constrained version of plaintext, and is described in
`PEP 12 <https://www.python.org/dev/peps/pep-0012/>`_.
The ``pep2html.py`` processing and installation script knows
how to produce the HTML for the PEP format.

To render the PEPs, you'll first need to install the requirements,
(preferably in a fresh virtual environment):

.. code-block:: console

    python -m pip install -r requirements.txt


Generating the PEP Index
========================

PEP 0 is automatically generated based on the metadata headers in other
PEPs. The script handling this is ``genpepindex.py``, with supporting
libraries in the ``pep0`` directory.


Checking PEP formatting and rendering
=====================================

Please don't commit changes with reStructuredText syntax errors that cause PEP
generation to fail, or result in major rendering defects relative to what you
intend. To check building the HTML output for your PEP (for example, PEP 12)
using the current default docutils-based system, run the ``pep2html.py`` script
with your PEP source file as its argument; e.g. for PEP 12,

.. code-block:: console

    python pep2html.py pep-0012.rst

If you're on a system with ``make``, you can instead execute, e.g.,

.. code-block:: console

    make pep-0012.rst

To generate HTML for all the PEPs, run the script/``make`` without a PEP
file argument.

By default, this will output a file (e.g. ``pep-0012.html``) in the root
directory, which you can view to see the HTML output of your PEP.
Note that the custom CSS stylesheet is not used by default, so
the PEP will look rather plain, but all the basic formatting produced by the
reStructuredText syntax in your source file should be visible.

You can also view your PEP locally with the Sphinx-based builder,
which will show the PEP exactly as it will appear on the preview
of the new rendering system proposed in :pep:`676`;
see `Rendering PEPs with Sphinx`_ for details.

Finally, you can check for and fix common linting and spelling issues,
either on-demand or automatically as you commit, with our pre-commit suite.
See the `Contributing Guide <./CONTRIBUTING.rst>`_ for details.


Generating HTML for Python.org
==============================

Python.org includes its own helper modules to render PEPs as HTML, with
suitable links back to the source pages in the version control repository.

These can be found `in the python.org repository
<https://github.com/python/pythondotorg/tree/main/peps>`__.

When making changes to the PEP management process that may impact python.org's
rendering pipeline:

* Clone the `python.org repository <https://github.com/python/pythondotorg/>`_.
* Get `set up for local python.org development
  <https://pythondotorg.readthedocs.io/install.html#manual-setup>`_.
* Adjust ``PEP_REPO_PATH`` in ``pydotorg/settings/local.py`` to refer to your
  local clone of the PEP repository.
* Run ``./manage.py generate_pep_pages`` as described the `python.org docs
  <https://pythondotorg.readthedocs.io/pep_generation.html>`__.


Rendering PEPs with Sphinx
==========================

There is a Sphinx-rendered version of the PEPs at https://python.github.io/peps/
(updated on every push to ``main``).

**Warning:** This version is not, and should not be taken to be, a canonical
source for PEPs whilst it remains in preview (please `report any rendering bugs
<https://github.com/python/peps/issues/new>`_).
The canonical source for PEPs remains https://www.python.org/dev/peps/


Build PEPs with Sphinx locally
------------------------------

See the `build documentation <./docs/build.rst>`__ for full step by step
instructions on how to install, build and view the rendered PEPs with Sphinx.

In summary, after installing the dependencies (preferably in a virtual
environment) with:

.. code-block:: console

    python -m pip install -r requirements.txt

You can build the PEPs with sphinx by running, if your system has ``make``:

.. code-block:: console

    make sphinx

Otherwise, execute the ``build.py`` script directly:

.. code-block:: console

    python build.py

The output HTML can be found under the ``build`` directory.


``build.py`` usage
------------------

For details on the command-line options to the ``build.py`` script, run:

.. code-block:: console

    python build.py --help
