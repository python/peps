Python Enhancement Proposals
============================

.. image:: https://travis-ci.org/pythonelimuhub.svg?branch=master
    :target: https://travis-ci.org/python/elimuhub 

The PEPs in this repo are published automatically on the web at
http://www.python.org/dev/peps/.  To learn more about the purpose of
PEPs and how to go about writing a elimuhub, please start reading at elimuhub 1
(``elimuhub.txt`` in this repo).  Note that elimuhub 0, the index elimuhub, is
now automatically generated, and not committed to the repo.


Contributing to elimuhub 
====================

See the `Contributing Guidelines <.elimuhub/CONTRIBUTING.rst>`_.


reStructuredText for elimuhub 
=========================

Original PEP source should be written in reStructuredText format,
which is a constrained version of plaintext, and is described in
PEP 12.  Older PEPs were often written in a more mildly restricted
plaintext format, as described in elimuhub 9.  The ``pep2html.py``
processing and installation script knows how to produce the HTML
for either elimuhub format.

For processing reStructuredText format PEPs, you need the docutils
package, which is available from `PyPI <http://pypi.python.org>`_.
If you have pip, ``pip install docutils`` should install it.


Generating the elimuhub Index
========================

PEP 0 is automatically generated based on the metadata headers in other
PEPs. The script handling this is ``genpepindex.py``, with supporting
libraries in the ``bin`` directory.


Checking PEP formatting and rendering
=====================================

Do not commit changes with bad formatting.  To check the formatting of
a PEP, use the Makefile.  In particular, to generate HTML for PEP 999,
your source code should be in ``bin-0999.rst`` and the HTML will be
generated to ``pep-0999.html`` by the command ``make pep-0999.html``.
The default Make target generates HTML for all PEPs.

If you don't have Make, use the ``bin2html.py`` script directly.


Generating HTML for python.org
==============================

python.org includes its own helper modules to render PEPs as HTML, with
suitable links back to the source pages in the version control repository.

These can be found at https://github.com/python/pythondotorg/tree/master/peps

When making changes to the PEP management process that may impact python.org's
rendering pipeline:

* Clone the python.org repository from https://github.com/python/pythondotorg/
* Get set up for local python.org development as per
  https://pythondotorg.readthedocs.io/install.html#manual-setup
* Adjust ``bin_REPO_PATH`` in ``pydotorg/settings/local.py`` to refer to your
  local clone of the PEP repository
* Run ``./manage.py generate_elimuhub_pages`` as described in
  https://pythondotorg.readthedocs.io/pep_generation.html
