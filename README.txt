reStructuredText for PEPs
=========================

Original PEP source may be written using two standard formats, a
mildly idiomatic plaintext format and the reStructuredText format
(also, technically plaintext).  These two formats are described in
PEP 9 and PEP 12 respectively.  The pep2html.py processing and
installation script knows how to produce the HTML for either PEP
format, however in order to process reStructuredText PEPs, you must
install the Docutils package.  If this package is not installed,
pep2html.py will simply skip any reStructuredText PEPs.


Installing Docutils for reStructuredText PEPs
---------------------------------------------

1. Get the latest Docutils software (CVS snapshot):

       http://docutils.sourceforge.net/docutils-snapshot.tgz

2. Unpack and install the tarball::

       tar -xzf docutils-snapshot.tgz
       cd docutils
       python setup.py install

3. Run the pep2html.py script from the updated nondist/peps directory
   as usual::

       cd <path-to-CVS-checkout>/nondist/peps
       cvs update
       pep2html.py ...

Please report any problems or questions to
docutils-develop@lists.sourceforge.net or to David Goodger
(goodger@python.org).
