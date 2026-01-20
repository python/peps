PEP: <REQUIRED: pep number>
Title: Virtual environment discovery
Author: Brett Cannon <brett@python.org>
Discussions-To: Pending
Status: Draft
Type: Standards Track
Created: 19-Jan-2026
Python-Version: 3.15
Post-History: Pending


Abstract
========

This PEP sets out to help make the discovery of a project's virtual environment
easier for tools by providing a default location as well as a way for a project
to point to its preferred virtual environment when it differs from the default
location.


Motivation
==========

Typically, when someone is working on a project larger than a single file, a
long-lived virtual environment is desirable (the single file case is covered by
:pep:`723`). As such, tools working on the user's behalf may want to create
and/or use the same virtual environment. These tools could be custom scripts in
the project like running the test script or 3rd-party tools like package
installers.

[Clearly explain why the existing language specification is inadequate to address the problem that the PEP solves.]


Rationale
=========

[Describe why particular design decisions were made.]


Specification
=============

[Describe the syntax and semantics of any new language feature.]


Backwards Compatibility
=======================

[Describe potential impact and severity on pre-existing code.]


Security Implications
=====================

[How could a malicious user take advantage of this new feature?]


How to Teach This
=================

[How to teach users, new and experienced, how to apply the PEP to their work.]


Reference Implementation
========================

[Link to any existing implementation and details about its state, e.g. proof-of-concept.]


Rejected Ideas
==============

[Why certain ideas that were brought while discussing this PEP were not ultimately pursued.]


Open Issues
===========

[Any points that are still being decided/discussed.]


Acknowledgements
================

[Thank anyone who has helped with the PEP.]


Footnotes
=========

[A collection of footnotes cited in the PEP, and a place to list non-inline hyperlink targets.]


Copyright
=========

This document is placed in the public domain or under the
CC0-1.0-Universal license, whichever is more permissive.
