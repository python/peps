Python Enhancement Proposals
============================

.. image:: https://github.com/python/peps/actions/workflows/build.yml/badge.svg
    :target: https://github.com/python/peps/actions

The PEPs in this repo are published automatically on the web at
https://www.python.org/dev/peps/.  To learn more about the purpose of
PEPs and how to go about writing a PEP, please start reading at PEP 1
(``pep-0001.txt`` in this repo).  Note that PEP 0, the index PEP, is
now automatically generated, and not committed to the repo.


Contributing to PEPs
====================

See the `Contributing Guidelines <./CONTRIBUTING.rst>`_.


reStructuredText for PEPs
=========================

Original PEP source should be written in reStructuredText format,
which is a constrained version of plaintext, and is described in
PEP 12.  Older PEPs were often written in a more mildly restricted
plaintext format, as described in PEP 9.  The ``pep2html.py``
processing and installation script knows how to produce the HTML
for either PEP format.

For processing reStructuredText format PEPs, you need the docutils
package, which is available from `PyPI <https://pypi.org/>`_.
If you have pip, ``pip install docutils`` should install it.


Generating the PEP Index
========================

PEP 0 is automatically generated based on the metadata headers in other
PEPs. The script handling this is ``genpepindex.py``, with supporting
libraries in the ``pep0`` directory.


Checking PEP formatting and rendering
=====================================

Avoid committing changes with reStructuredText syntax errors that cause PEP
generation to fail, or result in major rendering defects relative to what
you intend. To build the HTML output for your PEP (for example, PEP 12)
using the current default docutils-based system, run the ``pep2html.py`` script
with your PEP source file as its argument, e.g. for PEP 12,
``python -X dev pep2html.py pep-0012.rst``,
If you're on a system with ``make``, you can instead simply execute, e.g.,
``make pep-0012.rst``.
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


Generating HTML for python.org
==============================

python.org includes its own helper modules to render PEPs as HTML, with
suitable links back to the source pages in the version control repository.

These can be found at https://github.com/python/pythondotorg/tree/main/peps

When making changes to the PEP management process that may impact python.org's
rendering pipeline:

* Clone the python.org repository from https://github.com/python/pythondotorg/
* Get set up for local python.org development as per
  https://pythondotorg.readthedocs.io/install.html#manual-setup
* Adjust ``PEP_REPO_PATH`` in ``pydotorg/settings/local.py`` to refer to your
  local clone of the PEP repository
* Run ``./manage.py generate_pep_pages`` as described in
  https://pythondotorg.readthedocs.io/pep_generation.html


Rendering PEPs with Sphinx
==========================

There is a Sphinx-rendered version of the PEPs at https://python.github.io/peps/
(updated on every push to ``main``).

**Warning:** This version is not, and should not be taken to be, a canonical
source for PEPs whilst it remains in preview (`please report any rendering bugs
<https://github.com/python/peps/issues/new>`_). The canonical source for PEPs remains
https://www.python.org/dev/peps/

Build PEPs with Sphinx locally:
-------------------------------

1. Ensure you have Python >=3.9 and Sphinx installed
2. If you have access to ``make``, follow (i), otherwise (ii)

   i.  Run ``make sphinx-local``
   ii. Run ``python build.py -j 8 --build-files``. Note that the jobs argument
       only takes effect on unix (non-mac) systems.
3. Wait for Sphinx to render the PEPs. There may be a series of warnings about
   unreferenced citations or labels -- whilst these are valid warnings they do
   not impact the build process.
4. Navigate to the ``build`` directory of your PEPs repo to find the HTML pages.
   PEP 0 provides a formatted index, and may be a useful reference.

Arguments to ``build.py``:
--------------------------

Renderers:

``-f`` or ``--build-files``
    Renders PEPs to ``pep-XXXX.html`` files

``-d`` or ``--build-dirs``
    Renders PEPs to ``index.html`` files within ``pep-XXXX`` directories

Options:

``-i`` or ``--index-file``
    Copies PEP 0 to a base index file

``-j`` or ``--jobs``
    How many parallel jobs to run (if supported). Integer, default 1

``-n`` or ``--nitpicky``
    Runs Sphinx in `nitpicky` mode

``-w`` or ``--fail-on-warning``
    Fails Sphinx on warnings

Tools:

``-l`` or ``--check-links``
    Checks validity of links within PEP sources
