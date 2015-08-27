PEP: 470
Title: Removing External Hosting Support on PyPI
Version: $Revision$
Last-Modified: $Date$
Author: Donald Stufft <donald@stufft.io>,
BDFL-Delegate: TBD
Discussions-To: distutils-sig@python.org
Status: Draft
Type: Process
Content-Type: text/x-rst
Created: 12-May-2014
Post-History: 14-May-2014, 05-Jun-2014, 03-Oct-2014, 13-Oct-2014, 26-Aug-2015
Replaces: 438


Abstract
========

This PEP proposes the deprecation and removal of support for hosting files
externally to PyPI as well as the deprecation and removal of the functionality
added by PEP 438, particularly rel information to classify different types of
links and the meta-tag to indicate API version.


Rationale
=========

Historically PyPI did not have any method of hosting files nor any method of
automatically retrieving installables, it was instead focused on providing a
central registry of names, to prevent naming collisions, and as a means of
discovery for finding projects to use. In the course of time setuptools began
to scrape these human facing pages, as well as pages linked from those pages,
looking for things it could automatically download and install. Eventually this
became the "Simple" API which used a similar URL structure however it
eliminated any of the extraneous links and information to make the API more
efficient. Additionally PyPI grew the ability for a project to upload release
files directly to PyPI enabling PyPI to act as a repository in addition to an
index.

This gives PyPI two equally important roles that it plays in the Python
ecosystem, that of index to enable easy discovery of Python projects and
central repository to enable easy hosting, download, and installation of Python
projects. Due to the history behind PyPI and the very organic growth it has
experienced the lines between these two roles are blurry, and this blurring has
caused confusion for the end users of both of these roles and this has in turn
caused ire between people attempting to use PyPI in different capacities, most
often when end users want to use PyPI as a repository but the author wants to
use PyPI solely as an index.

This confusion comes down to end users of projects not realizing if a project
is hosted on PyPI or if it relies on an external service. This often manifests
itself when the external service is down but PyPI is not. People will see that
PyPI works, and other projects works, but this one specific one does not. They
often times do not realize who they need to contact in order to get this fixed
or what their remediation steps are.

PEP 438 attempted to solve this issue by allowing projects to explicitly
declare if they were using the repository features or not, and if they were
not, it had the installers classify the links it found as either "internal",
"verifiable external" or "unverifiable external". PEP 438 was accepted and
implemented in pip 1.4 (released on Jul 23, 2013) with the final transition
implemented in pip 1.5 (released on Jan 2, 2014).

PEP 438 was successful in bringing about more people to utilize PyPI's
repository features, an altogether good thing given the global CDN powering
PyPI providing speed ups for a lot of people, however it did so by introducing
a new point of confusion and pain for both the end users and the authors.

By moving to using explicit multiple repositories we can make the lines between
these two roles much more explicit and remove the "hidden" surprises caused by
the current implementation of handling people who do not want to use PyPI as a
repository.


Key User Experience Expectations
--------------------------------

#. Easily allow external hosting to "just work" when appropriately configured
   at the system, user or virtual environment level.
#. Eliminate any and all references to the confusing "verifiable external" and
   "unverifiable external" distinction from the user experience (both when
   installing and when releasing packages).
#. The repository aspects of PyPI should become *just* the default package
   hosting location (i.e. the only one that is treated as opt-out rather than
   opt-in by most client tools in their default configuration). Aside from that
   aspect, hosting on PyPI should not otherwise provide an enhanced user
   experience over hosting your own package repository.
#. Do all of the above while providing default behaviour that is secure against
   most attackers below the nation state adversary level.


Why Additional Repositories?
----------------------------

The two common installer tools, pip and easy_install/setuptools, both support
the concept of additional locations to search for files to satisfy the
installation requirements and have done so for many years. This means that
there is no need to "phase" in a new flag or concept and the solution to
installing a project from a repository other than PyPI will function regardless
of how old (within reason) the end user's installer is. Not only has this
concept existed in the Python tooling for some time, but it is a concept that
exists across languages and even extending to the OS level with OS package
tools almost universally using multiple repository support making it extremely
likely that someone is already familiar with the concept.

Additionally, the multiple repository approach is a concept that is useful
outside of the narrow scope of allowing projects that wish to be included on
the index portion of PyPI but do not wish to utilize the repository portion of
PyPI. This includes places where a company may wish to host a repository that
contains their internal packages or where a project may wish to have multiple
"channels" of releases, such as alpha, beta, release candidate, and final
release. This could also be used for projects wishing to host files which
cannot be uploaded to PyPI, such as multi-gigabyte data files or, currently at
least, Linux Wheels.


Why Not PEP 438 or Similar?
---------------------------

While the additional search location support has existed in pip and setuptools
for quite some time support for PEP 438 has only existed in pip since the 1.4
version, and still has yet to be implemented in setuptools. The design of
PEP 438 did mean that users still benefited for projects which did not require
external files even with older installers, however for projects which *did*
require external files, users are still silently being given either potentially
unreliable or, even worse, unsafe files to download. This system is also unique
to Python as it arises out of the history of PyPI, this means that it is almost
certain that this concept will be foreign to most, if not all users, until they
encounter it while attempting to use the Python toolchain.

Additionally, the classification system proposed by PEP 438 has, in practice,
turned out to be extremely confusing to end users, so much so that it is a
position of this PEP that the situation as it stands is completely untenable.
The common pattern for a user with this system is to attempt to install a
project possibly get an error message (or maybe not if the project ever
uploaded something to PyPI but later switched without removing old files), see
that the error message suggests ``--allow-external``, they reissue the command
adding that flag most likely getting another error message, see that this time
the error message suggests also adding ``--allow-unverified``, and again issue
the command a third time, this time finally getting the thing they wish to
install.

This UX failure exists for several reasons.

#. If pip can locate files at all for a project on the Simple API it will
   simply use that instead of attempting to locate more. This is generally the
   right thing to do as attempting to locate more would erase a large part of
   the benefit of PEP 438. This means that if a project *ever* uploaded a file
   that matches what the user has requested for install that will be used
   regardless of how old it is.
#. PEP 438 makes an implicit assumption that most projects would either upload
   themselves to PyPI or would update themselves to directly linking to release
   files. While a large number of projects did ultimately decide to upload to
   PyPI, some of them did so only because the UX around what PEP 438 was so bad
   that they felt forced to do so. More concerning however, is the fact that
   very few projects have opted to directly and safely link to files and
   instead they still simply link to pages which must be scraped in order to
   find the actual files, thus rendering the safe variant
   (``--allow-external``) largely useless.
#. Even if an author wishes to directly link to their files, doing so safely is
   non-obvious. It requires the inclusion of a MD5 hash (for historical
   reasons) in the hash of the URL. If they do not include this then their
   files will be considered "unverified".
#. PEP 438 takes a security centric view and disallows any form of a global opt
   in for unverified projects. While this is generally a good thing, it creates
   extremely verbose and repetitive command invocations such as::

      $ pip install --allow-external myproject --allow-unverified myproject myproject
      $ pip install --allow-all-external --allow-unverified myproject myproject


Multiple Repository/Index Support
=================================

Installers SHOULD implement or continue to offer, the ability to point the
installer at multiple URL locations. The exact mechanisms for a user to
indicate they wish to use an additional location is left up to each individual
implementation.

Additionally the mechanism discovering an installation candidate when multiple
repositories are being used is also up to each individual implementation,
however once configured an implementation should not discourage, warn, or
otherwise cast a negative light upon the use of a repository simply because it
is not the default repository.

Currently both pip and setuptools implement multiple repository support by
using the best installation candidate it can find from either repository,
essentially treating it as if it were one large repository.

Installers SHOULD also implement some mechanism for removing or otherwise
disabling use of the default repository. The exact specifics of how that is
achieved is up to each individual implementation.

Installers SHOULD also implement some mechanism for whitelisting and
blacklisting which projects a user wishes to install from a particular
repository. The exact specifics of how that is achieved is up to each
individual implementation.


Deprecation and Removal of Link Spidering
=========================================

A new hosting mode will be added to PyPI. This hosting mode will be called
``pypi-only`` and will be in addition to the three that PEP 438 has already
given us which are ``pypi-explicit``, ``pypi-scrape``, ``pypi-scrape-crawl``.
This new hosting mode will modify a project's simple api page so that it only
lists the files which are directly hosted on PyPI and will not link to anything
else.

Upon acceptance of this PEP and the addition of the ``pypi-only`` mode, all new
projects will be defaulted to the PyPI only mode and they will be locked to
this mode and unable to change this particular setting.

An email will then be sent out to all of the projects which are hosted only on
PyPI informing them that in one month their project will be automatically
converted to the ``pypi-only`` mode. A month after these emails have been sent
any of those projects which were emailed, which still are hosted only on PyPI
will have their mode set permanently to ``pypi-only``.

At the same time, an email will be sent to projects which rely on hosting
external to PyPI. This email will warn these projects that externally hosted
files have been deprecated on PyPI and that in 3 months from the time of that
email that all external links will be removed from the installer APIs. This
email **MUST** include instructions for converting their projects to be hosted
on PyPI and **MUST** include links to a script or package that will enable them
to enter their PyPI credentials and package name and have it automatically
download and re-host all of their files on PyPI. This email **MUST** also
include instructions for setting up their own index page. This email must also contain a link to the Terms of Service for PyPI as many users may have signed
up a long time ago and may not recall what those terms are. Finally this email
must also contain a list of the links registered with PyPI where we were able
to detect an installable file was located.

Two months after the initial email, another email must be sent to any projects
still relying on external hosting. This email will include all of the same
information that the first email contained, except that the removal date will
be one month away instead of three.

Finally a month later all projects will be switched to the ``pypi-only`` mode
and PyPI will be modified to remove the externally linked files functionality.


Summary of Changes
==================

Repository side
---------------

#. Deprecate and remove the hosting modes as defined by PEP 438.
#. Restrict simple API to only list the files that are contained within the
   repository.


Client side
-----------

#. Implement multiple repository support.
#. Implement some mechanism for removing/disabling the default repository.
#. Deprecate / Remove PEP 438


Impact
======

To determine impact, we've looked at all projects using a method of searching
PyPI which is similar to what pip and setuptools use and searched for all
files available on PyPI, safely linked from PyPI, unsafely linked from PyPI,
and finally unsafely available outside of PyPI. When the same file was found
in multiple locations it was deduplicated and only counted it in one location
based on the following preferences: PyPI > Safely Off PyPI > Unsafely Off PyPI.
This gives us the broadest possible definition of impact, it means that any
single file for this project may no longer be visible by default, however that
file could be years old, or it could be a binary file while there is a sdist
available on PyPI. This means that the *real* impact will likely be much
smaller, but in an attempt not to miscount we take the broadest possible
definition.

At the time of this writing there are 65,232 projects hosted on PyPI and of
those, 59 of them rely on external files that are safely hosted outside of PyPI
and 931 of them rely on external files which are unsafely hosted outside of
PyPI. This shows us that 1.5% of projects will be affected in some way by this
change while 98.5% will continue to function as they always have. In addition,
only 5% of the projects affected are using the features provided by PEP 438 to
safely host outside of PyPI while 95% of them are exposing their users to
Remote Code Execution via a Man In The Middle attack.


Data Sovereignty
================

In the discussions around previous versions of this PEP, one of the key use
cases for wanting to host files externally to PyPI was due to data sovereignty
requirements for people living in jurisdictions outside of the USA, where PyPI
is currently hosted. The author of this PEP is not blind to these concerns and
realizes that this PEP represents a regression for the people that have these
concerns, however the current situation is presenting an extremely poor user
experience and the feature is only being used by a small percentage of
projects. In addition, the data sovereignty problems requires familarity with
the laws outside of the home jurisdiction of the author of this PEP, who is
also the principal developer and operator of PyPI. For these reasons, a
solution for the problem of data sovereignty has been deferred and is
considered outside of the scope for this PEP.

The data sovereignty issue will need to  be addressed by someone with an
understanding of the restrictions and constraints involved. As the author of
this PEP does not have that expertise, it should be addressed in a separate
PEP.


Rejected Proposals
==================

Allow easier discovery of externally hosted indexes
---------------------------------------------------

A previous version of this PEP included a new feature added to both PyPI and
installers that would allow project authors to enter into PyPI a list of
URLs that would instruct installers to ignore any files uploaded to PyPI and
instead return an error telling the end user about these extra URLs that they
can add to their installer to make the installation work.

This idea is rejected because it provides a similar painful end user experience
where people will first attempt to install something, get an error, then have
to re-run the installation with the correct options.


Keep the current classification system but adjust the options
-------------------------------------------------------------

This PEP rejects several related proposals which attempt to fix some of the
usability problems with the current system but while still keeping the general
gist of PEP 438.

This includes:

* Default to allowing safely externally hosted files, but disallow unsafely
  hosted.

* Default to disallowing safely externally hosted files with only a global flag
  to enable them, but disallow unsafely hosted.

* Continue on the suggested path of PEP 438 and remove the option to unsafely
  host externally but continue to allow the option to safely host externally.

These proposals are rejected because:

* The classification system introduced in PEP 438 in an entirely unique concept
  to PyPI which is not generically applicable even in the context of Python
  packaging. Adding additional concepts comes at a cost.

* The classification system itself is non-obvious to explain and to
  pre-determine what classification of link a project will require entails
  inspecting the project's ``/simple/<project>/`` page, and possibly any URLs
  linked from that page.

* The ability to host externally while still being linked for automatic
  discovery is mostly a historic relic which causes a fair amount of pain and
  complexity for little reward.

* The installer's ability to optimize or clean up the user interface is limited
  due to the nature of the implicit link scraping which would need to be done.
  This extends to the ``--allow-*`` options as well as the inability to
  determine if a link is expected to fail or not.

* The mechanism paints a very broad brush when enabling an option, while
  PEP 438 attempts to limit this with per package options. However a project
  that has existed for an extended period of time may often times have several
  different URLs listed in their simple index. It is not unusual for at least
  one of these to no longer be under control of the project. While an
  unregistered domain will sit there relatively harmless most of the time, pip
  will continue to attempt to install from it on every discovery phase. This
  means that an attacker simply needs to look at projects which rely on unsafe
  external URLs and register expired domains to attack users.


Implement this PEP, but Do Not Remove the Existing Links
--------------------------------------------------------

This is essentially the backwards compatible version of this PEP. It attempts
to allow people using older clients, or clients which do not implement this
PEP to continue on as if nothing had changed. This proposal is rejected because
the vast bulk of those scenarios are unsafe uses of the deprecated features. It
is the opinion of this PEP that silently allowing unsafe actions to take place
on behalf of end users is simply not an acceptable solution.


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
