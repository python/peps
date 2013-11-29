Python Enhancement Proposals
============================

The PEPs in this repo are published automatically on the web at
http://www.python.org/dev/peps/.  To learn more about the purpose of
PEPs and how to go about writing a PEP, please start reading at PEP 1
(pep-0001.txt in this repo).  Note that PEP 0, the index PEP, is now
automatically generated, and not committed to the repo.


reStructuredText for PEPs
=========================

Original PEP source may be written using two standard formats, a
mildly idiomatic plaintext format and the reStructuredText format
(also, technically plaintext).  These two formats are described in
PEP 9 and PEP 12 respectively.  The pep2html.py processing and
installation script knows how to produce the HTML for either PEP
format.

For processing reStructuredText format PEPs, you need the docutils
package, which is available from PyPI (http://pypi.python.org).
If you have pip, "pip install docutils" should install it.


Generating HTML
===============

Do not commit changes with bad formatting.  To check the formatting of
a PEP, use the Makefile.  In particular, to generate HTML for PEP 999,
your source code should be in pep-0999.txt and the HTML will be
generated to pep-0999.html by the command "make pep-0999.html".  The
default Make target generates HTML for all PEPs.  If you don't have
Make, use the pep2html.py script.
