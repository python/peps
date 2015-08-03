PEP: 0496
Title: Environment Markers
Version: $Revision$
Last-Modified: $Date$
Author: James Polley <jp@jamezpolley.com>
BDFL-Delegate: Nick Coghlan <ncoghlan@gmail.com>
Status: Draft
Type: Informational
Content-Type: text/x-rst
Created: 03-Jul-2015


Abstract
========

An **environment marker** describes a condition about the current execution
environment. They are used to indicate when certain dependencies are only
required in particular environments, and to indicate supported platforms
for distributions with additional constraints beyond the availability of a
Python runtime.

Environment markers were first specified in PEP-0345[1]. PEP-0426[2] (which
would replace PEP-0345) proposed extensions to the markers. When
2.7.10 was released, even these extensions became insufficient due to
their reliance on simple lexical comparisons, and thus this PEP has
been born.


Rationale
=========

Many Python packages are written with portability in mind.

For many packages this means they aim to support a wide range of
Python releases. If they depend on libraries such as ``argparse`` -
which started as external libraries, but later got incorporated into
core - specifying a single set of requirements is difficult, as the
set of required packages differs depending on the version of Python in
use.

For other packages, designing for portability means supporting
multiple operating systems. However, the significant differences
between them may mean that particular dependencies are only needed on
particular platforms (relying on ``pywin32`` only on Windows, for
example)"

Environment Markers attempt to provide more flexibility in a list of
requirements by allowing the developer to list requirements that are
specific to a particular environment.

Examples
========

Here are some examples of such markers inside a requirements.txt::

   pywin32 >=1.0 ; sys_platform == 'win32'
   unittest2 >=2.0,<3.0 ; python_version == '2.4' or python_version == '2.5'
   backports.ssl_match_hostname >= 3.4 ; python_version < '2.7.9' or (python_version >= '3.0' and python_version < '3.4')

And here's an example of some conditional metadata included in
setup.py for a distribution that requires PyWin32 both at runtime and
buildtime when using Windows::

   setup(
     install_requires=["pywin32 > 1.0 : sys.platform == 'win32'"],
     setup_requires=["pywin32 > 1.0 : sys.platform == 'win32'"]
     )


Micro-language
==============

The micro-language behind this is as follows. It compares:

* strings with the ``==`` and ``in`` operators (and their opposites)
* version numbers with the ``<``, ``<=``, ``>=``, and ``<`` operators
  in addition to those supported for strings

The usual boolean operators ``and`` and ``or`` can be used to combine
expressions, and parentheses are supported for grouping.

The pseudo-grammar is ::

    MARKER: EXPR [(and|or) EXPR]*
    EXPR: ("(" MARKER ")") | (STREXPR|VEREXPR)
    STREXPR: STRING [STRCMPOP STREXPR]
    STRCMPOP: ==|!=|in|not in
    VEREXPR: VERSION [VERCMPOP VEREXPR]
    VERCMPOP: (==|!=|<|>|<=|>=)


``SUBEXPR`` is either a Python string (such as ``'win32'``) or one of
the ``Strings`` marker variables listed below.

``VEREXPR`` is a PEP-0440[3] version identifier, or one of the
``Version number`` marker variables listed below. Comparisons between
version numbers are done using PEP-0440 semantics.


Strings
-------

* ``os_name``: ``os.name``
* ``sys_platform``: ``sys.platform``
* ``platform_release``: ``platform.release()``
* ``implementation_name``: ``sys.implementation.name``
* ``platform_machine``: ``platform.machine()``
* ``platform_python_implementation``: ``platform.python_implementation()``


If a particular string value is not available (such as ``sys.implementation.name``
in versions of Python prior to 3.3), the corresponding marker
variable MUST be considered equivalent to the empty string.

If a particular version number value is not available (such as
``sys.implementation.version`` in versions of Python prior to 3.3) the
corresponding marker variable MUST be considered equivalent to ``0``


Version numbers
---------------

* ``python_version``: ``platform.python_version()[:3]``
* ``python_full_version``: see definition below
* ``platform_version``: ``platform.version()``
* ``implementation_version````: see definition below

The ``python_full_version`` and ``implementation_version`` marker variables
are derived from ``sys.version_info`` and ``sys.implementation.version``
respectively, in accordance with the following algorithm::

    def format_full_version(info):
        version = '{0.major}.{0.minor}.{0.micro}'.format(info)
        kind = info.releaselevel
        if kind != 'final':
            version += kind[0] + str(info.serial)
        return version

    python_full_version = format_full_version(sys.version_info)
    implementation_version = format_full_version(sys.implementation.version)

``python_full_version`` will typically correspond to ``sys.version.split()[0]``.


References
==========

.. [1] PEP 345, Metadata for Python Software Packages 1.2, Jones
   (http://www.python.org/dev/peps/pep-0345)

.. [2] PEP 0426, Metadata for Python Software Packages 2.0, Coghlan, Holth, Stufft
   (http://www.python.org/dev/peps/pep-0426)

.. [3] PEP 0440, Version Identification and Dependency Specification, Coghlan, Stufft
   (https://www.python.org/dev/peps/pep-0440/)

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
