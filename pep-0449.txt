PEP: 449
Title: Removal of Official Public PyPI Mirrors
Version: $Revision$
Last-Modified: $Date$
Author: Donald Stufft <donald@stufft.io>
BDFL-Delegate: Richard Jones <richard@python.org>
Discussions-To: distutils-sig@python.org
Status: Draft
Type: Process
Content-Type: text/x-rst
Created: 04-Aug-2013
Post-History: 04-Aug-2013
Replaces: 381


Abstract
========

This PEP provides a path to deprecate and ultimately remove the official
public mirroring infrastructure for `PyPI`_. It does not propose the removal
of mirroring support in general.


Rationale
=========

The PyPI mirroring infrastructure (defined in `PEP381`_) provides a means to
mirror the content of PyPI used by the automatic installers. It also provides
a method for autodiscovery of mirrors and a consistent naming scheme.

There are a number of problems with the official public mirrors:

* They give control over a \*.python.org domain name to a third party,
  allowing that third party to set or read cookies on the pypi.python.org and
  python.org domain name.
* The use of a sub domain of pypi.python.org means that the mirror operators
  will never be able to get a SSL certificate of their own, and giving them
  one for a python.org domain name is unlikely to happen.
* They are often out of date, most often by several hours to a few days, but
  regularly several days and even months.
* With the introduction of the CDN on PyPI the public mirroring infrastructure
  is not as important as it once was as the CDN is also a globally distributed
  network of servers which will function even if PyPI is down.
* Although there is provisions in place for it, there is currently no known
  installer which uses the authenticity checks discussed in `PEP381`_ which
  means that any download from a mirror is subject to attack by a malicious
  mirror operator, but further more due to the lack of TLS it also means that
  any download from a mirror is also subject to a MITM attack.
* They have only ever been implemented by one installer (pip), and its
  implementation, besides being insecure, has serious issues with performance
  and is slated for removal with it's next release (1.5).

Due to the number of issues, some of them very serious, and the CDN which more
or less provides much of the same benefits this PEP proposes to first
deprecate and then remove the public mirroring infrastructure. The ability to
mirror and the method of mirroring will not be affected and the existing
public mirrors are encouraged to acquire their own domains to host their
mirrors on if they wish to continue hosting them.


Plan for Deprecation & Removal
==============================

Immediately upon acceptance of this PEP documentation on PyPI will be updated
to reflect the deprecated nature of the official public mirrors and will
direct users to external resources like http://www.pypi-mirrors.org/ to
discover unofficial public mirrors if they wish to use one.

On October 1st, 2013, roughly 2 months from the date of this PEP, the DNS names
of the public mirrors ([a-g].pypi.python.org) will be changed to point back to
PyPI which will be modified to accept requests from those domains. At this
point in time the public mirrors will be considered deprecated.

Then, roughly 2 months after the release of the first version of pip to have
mirroring support removed (currently slated for pip 1.5) the DNS entries for
[a-g].pypi.python.org and last.pypi.python.org will be removed and PyPI will
no longer accept requests at those domains.


Unofficial Public or Private Mirrors
====================================

The mirroring protocol will continue to exist as defined in `PEP381`_ and
people are encouraged to utilize to host unofficial public and private mirrors
if they so desire. For operators of unofficial public or private mirrors the
recommended mirroring client is `Bandersnatch`_.


.. _PyPI: https://pypi.python.org/
.. _PEP381: http://www.python.org/dev/peps/pep-0381/
.. _Bandersnatch: https://pypi.python.org/pypi/bandersnatch


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
