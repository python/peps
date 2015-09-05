PEP: 503
Title: Simple Repository API
Version: $Revision$
Last-Modified: $Date$
Author: Donald Stufft <donald@stufft.io>
BDFL-Delegate: Donald Stufft <donald@stufft.io>
Discussions-To: distutils-sig@python.org
Status: Draft
Type: Informational
Content-Type: text/x-rst
Created: 04-Sep-2015
Post-History: 04-Sep-2015


Abstract
========

There are many implementations of a Python package repository and many tools
that consume them. Of these, the cannonical implementation that defines what
the "simple" repository API looks like is the implementation that powers
PyPI. This document will specify that API, documenting what the correct
behavior for any implementation of the simple repository API.


Specification
=============

A repository that implements the simple API is defined by its base url, this is
the top level URL that all additional URLS are below. The API is named the
"simple" repository due to fact that PyPI's base URL is
``https://pypi.python.org/simple/``.

.. note:: All subsequent URLs in this document will be relative to this base
          URL (so given PyPI's URL, an URL of ``/foo/`` would be
          ``https://pypi.python.org/simple/foo/``.


Within a repository, the root URL (``/``) **MUST** be a valid HTML5 page with a
single anchor element per project in the repository. The text of the anchor tag
**MUST** be the normalized name of the project and the href attribute **MUST**
link to the URL for that particular project. As an example::

   <!DOCTYPE html>
   <html>
     <body>
       <a href="/frob/">frob</a>
       <a href="/spamspamspam/">spamspamspam</a>
     </body>
   </html>

Below the root URL is another URL for each individual project contained within
a repository. The format of this URL is ``/<project>/`` where the ``<project>``
is replaced by the normalized name for that project, so a project named
"HolyGrail" would have an URL like ``/holygrail/``. This URL must response with
a valid HTML5 page with a single anchor element per file for the project. The
text of the anchor tag **MUST** be the filename of the file and the href
attribute **MUST** be an URL that links to the location of the file for
download. The URL **SHOULD** include a hash in the form of an URL fragment with
the following syntax: ``#<hashname>=<hashvalue>``, where ``<hashname>`` is the
lowercase name of the hash function (such as ``sha256``) and ``<hashvalue>`` is
the hex encoded digest.

In addition to the above, the following constraints are placed on the API:

* All URLs **MUST** end with a ``/`` and the repository **SHOULD** redirect the
  URLs without a ``/`` to add a ``/`` to the end.

* There is no constraints on where the files must be hosted relative to the
  repository.

* There may be any other HTML elements on the API pages as long as the required
  anchor elements exist.

* Repositories **MAY** redirect unnormalized URLs to the cannonical normalized
  URL (e.g. ``/Foobar/`` may redirect to ``/foobar/``), however clients
  **MUST NOT** rely on this redirection and **MUST** request the normalized
  URL.

* Repositories **SHOULD** choose a hash function from one of the ones
  guarenteed to be available via the ``hashlib`` module in the Python standard
  library (currently ``md5``, ``sha1``, ``sha224``, ``sha256``, ``sha384``,
  ``sha512``). The current recommendation is to use ``sha256``.


Normalized Names
----------------

This PEP references the concept of a "normalized" project name. As per PEP 426
the only valid characters in a name are the ASCII alphabet, ASCII numbers,
``.``, ``-``, and ``_``. The name should be lowercased with all runs of the
characters ``.``, ``-``, or ``_`` replaced with a single ``-`` character. This
can be implemented in Python with the ``re`` module::

   import re

   def normalize(name):
       return re.sub(r"[-_.]+", "-", name).lower()


Copyright
=========

This document has been placed in the public domain.



..
   Local Variables:
   mode: indented-text
   indent-tabs-mode: nil
   sentence-end-double-space: t
   fill-column: 70
   coding: utf-8
   End:
