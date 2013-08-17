PEP: 449
Title: Removal of the PyPI Mirror Auto Discovery and Naming Scheme
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

This PEP provides a path to deprecate and ultimately remove the auto discovery
of PyPI mirrors as well as the hard coded naming scheme which requires
delegating a domain name under pypi.python.org to a third party.


Rationale
=========

The PyPI mirroring infrastructure (defined in `PEP381`_) provides a means to
mirror the content of PyPI used by the automatic installers. It also provides
a method for auto discovery of mirrors and a consistent naming scheme.

There are a number of problems with the auto discovery protocol and the
naming scheme:

* They give control over a \*.python.org domain name to a third party,
  allowing that third party to set or read cookies on the pypi.python.org and
  python.org domain name.
* The use of a sub domain of pypi.python.org means that the mirror operators
  will never be able to get a SSL certificate of their own, and giving them
  one for a python.org domain name is unlikely to happen.
* The auto discovery uses an unauthenticated protocol (DNS).
* The lack of a TLS certificate on these domains means that clients can not
  be sure that they have not been a victim of DNS poisoning or a MITM attack.
* The auto discovery protocol was designed to enable a client to automatically
  select a mirror for use. This is no longer a requirement because the CDN
  that PyPI is now using a globally distributed network of servers which will
  automatically select one close to the client without any effort on the
  clients part.
* The auto discovery protocol and use of the consistent naming scheme has only
  ever been implemented by one installer (pip), and its implementation, besides
  being insecure, has serious issues with performance and is slated for removal
  with it's next release (1.5).
* While there are provisions in `PEP381`_ that would solve *some* of these
  issues for a dedicated client it would not solve the issues that affect a
  users browser. Additionally these provisions have not been implemented by
  any installer to date.

Due to the number of issues, some of them very serious, and the CDN which
provides most of the benefit of the auto discovery and consistent naming scheme
this PEP proposes to first deprecate and then remove the [a..z].pypi.python.org
names for mirrors and the last.pypi.python.org name for the auto discovery
protocol. The ability to mirror and the method of mirror will not be affected
and will continue to exist as written in `PEP381`_. Operators of existing
mirrors are encouraged to acquire their own domains and certificates to use for
their mirrors if they wish to continue hosting them.


Plan for Deprecation & Removal
==============================

Immediately upon acceptance of this PEP documentation on PyPI will be updated
to reflect the deprecated nature of the official public mirrors and will
direct users to external resources like http://www.pypi-mirrors.org/ to
discover unofficial public mirrors if they wish to use one.

Mirror operators, if they wish to continue operating their mirror, should
acquire a domain name to represent their mirror and, if they are able, a TLS
certificate. Once they have acquired a domain they should redirect their
assigned N.pypi.python.org domain name to their new domain. On Feb 15th, 2014
the DNS entries for [a..z].pypi.python.org and last.pypi.python.org will be
removed. At any time prior to Feb 15th, 2014 a mirror operator may request
that their domain name be reclaimed by PyPI and pointed back at the master.


Why Feb 15th, 2014
------------------

The most critical decision of this PEP is the final cut off date. If the date
is too soon then it needlessly punishes people by forcing them to drop
everything to update their deployment scripts. If the date is too far away then
the extended period of time does not help with the migration effort and merely
puts off the migration until a later date.

The date of Feb 15th, 2014 has been chosen because it is roughly 6 months from
the date of the PEP. This should ensure a lengthy period of time to enable
people to update their deployment procedures to point to the new domains names
without merely padding the cut off date.


Why the DNS entries must be removed
-----------------------------------

While it would be possible to simply reclaim the domain names used in mirror
and direct them back at PyPI in order to prevent users from needing to update
configurations to point away from those domains this has a number of issues.

* Anyone who currently has these names hard coded in their configuration has
  them hard coded as HTTP. This means that by allowing these names to continue
  resolving we make it simple for a MITM operator to attack users by rewriting
  the redirect to HTTPS prior to giving it to the client.
* The overhead of maintaining several domains pointing at PyPI has proved
  troublesome for the small number of N.pypi.python.org domains that have
  already been reclaimed. They often times get mis-configured when things
  change on the service which often leaves them broken for months at a time
  until somebody notices. By leaving them in we leave users of these domains
  open to random breakages which are less likely to get caught or noticed.
* People using these domains have explicitly chosen to use them for one reason
  or another. One such reason may be because they do not wish to deploy from
  a host located in a particular country. If these domains continue to resolve
  but do not point at their existing locations we have silently removed this
  choice from the existing users of those domains.

That being said, removing the entries *will* require users who have modified
their configuration to either point back at the master (PyPI) or select a new
mirror name to point at. This is regarded as a regrettable requirement to
protect PyPI itself and the users of the mirrors from the attacks outlined
above or, at the very least, require them to make an informed decision about
the insecurity.


Public or Private Mirrors
=========================

The mirroring protocol will continue to exist as defined in `PEP381`_ and
people are encouraged to to host public and private mirrors if they so desire.
The recommended mirroring client is `Bandersnatch`_.


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
