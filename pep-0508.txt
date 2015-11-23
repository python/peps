PEP: 508
Title: Dependency specification for Python Software Packages
Version: $Revision$
Last-Modified: $Date$
Author: Robert Collins <rbtcollins@hp.com>
BDFL-Delegate: Donald Stufft <donald@stufft.io>
Discussions-To: distutils-sig <distutils-sig@python.org>
Status: Accepted
Type: Standards Track
Content-Type: text/x-rst
Created: 11-Nov-2015
Post-History: 05-Nov-2015, 16-Nov-2015
Resolution: https://mail.python.org/pipermail/distutils-sig/2015-November/027868.html


Abstract
========

This PEP specifies the language used to describe dependencies for packages.
It draws a border at the edge of describing a single dependency - the
different sorts of dependencies and when they should be installed is a higher
level problem. The intent is to provide a building block for higher layer
specifications.

The job of a dependency is to enable tools like pip [#pip]_ to find the right
package to install. Sometimes this is very loose - just specifying a name, and
sometimes very specific - referring to a specific file to install. Sometimes
dependencies are only relevant in one platform, or only some versions are
acceptable, so the language permits describing all these cases.

The language defined is a compact line based format which is already in
widespread use in pip requirements files, though we do not specify the command
line option handling that those files permit. There is one caveat - the
URL reference form, specified in PEP-440 [#pep440]_ is not actually
implemented in pip, but since PEP-440 is accepted, we use that format rather
than pip's current native format.

Motivation
==========

Any specification in the Python packaging ecosystem that needs to consume
lists of dependencies needs to build on an approved PEP for such, but
PEP-426 [#pep426]_ is mostly aspirational - and there are already existing
implementations of the dependency specification which we can instead adopt.
The existing implementations are battle proven and user friendly, so adopting
them is arguably much better than approving an aspirational, unconsumed, format.

Specification
=============

Examples
--------

All features of the language shown with a name based lookup::

    requests [security,tests] >= 2.8.1, == 2.8.* ; python_version < "2.7.10"

A minimal URL based lookup::

    pip @ https://github.com/pypa/pip/archive/1.3.1.zip#sha1=da9234ee9982d4bbb3c72346a6de940a148ea686

Concepts
--------

A dependency specification always specifies a distribution name. It may
include extras, which expand the dependencies of the named distribution to
enable optional features. The version installed can be controlled using
version limits, or giving the URL to a specific artifact to install. Finally
the dependency can be made conditional using environment markers.

Grammar
-------

We first cover the grammar briefly and then drill into the semantics of each
section later.

A distribution specification is written in ASCII text. We use a parsley
[#parsley]_ grammar to provide a precise grammar. It is expected that the
specification will be embedded into a larger system which offers framing such
as comments, multiple line support via continuations, or other such features.

The full grammar including annotations to build a useful parse tree is
included at the end of the PEP.

Versions may be specified according to the PEP-440 [#pep440]_ rules. (Note:
URI is defined in std-66 [#std66]_::

    version_cmp   = wsp* '<' | '<=' | '!=' | '==' | '>=' | '>' | '~=' | '==='
    version       = wsp* ( letterOrDigit | '-' | '_' | '.' | '*' | '+' | '!' )+
    version_one   = version_cmp version wsp*
    version_many  = version_one (wsp* ',' version_one)*
    versionspec   = ( '(' version_many ')' ) | version_many
    urlspec       = '@' wsp* <URI_reference>

Environment markers allow making a specification only take effect in some
environments::

    marker_op     = version_cmp | (wsp* 'in') | (wsp* 'not' wsp+ 'in')
    python_str_c  = (wsp | letter | digit | '(' | ')' | '.' | '{' | '}' |
                     '-' | '_' | '*' | '#' | ':' | ';' | ',' | '/' | '?' |
                     '[' | ']' | '!' | '~' | '`' | '@' | '$' | '%' | '^' |
                     '&' | '=' | '+' | '|' | '<' | '>' )
    dquote        = '"'
    squote        = '\\''
    python_str    = (squote (python_str_c | dquote)* squote |
                     dquote (python_str_c | squote)* dquote)
    env_var       = ('python_version' | 'python_full_version' |
                     'os_name' | 'sys_platform' | 'platform_release' |
                     'platform_system' | 'platform_version' |
                     'platform_machine' | 'python_implementation' |
                     'implementation_name' | 'implementation_version' |
                     'extra' # ONLY when defined by a containing layer
                     )
    marker_var    = wsp* (env_var | python_str)
    marker_expr   = marker_var marker_op marker_var
                  | wsp* '(' marker wsp* ')'
    marker_and    = marker_expr wsp* 'and' marker_expr
                  | marker_expr
    marker_or     = marker_and wsp* 'or' marker_and
                      | marker_and
    marker        = marker_or
    quoted_marker = ';' wsp* marker

Optional components of a distribution may be specified using the extras
field::

    identifier    = letterOrDigit (
                    letterOrDigit |
                    (( letterOrDigit | '-' | '_' | '.')* letterOrDigit ) )*
    name          = identifier
    extras_list   = identifier (wsp* ',' wsp* identifier)*
    extras        = '[' wsp* extras_list? wsp* ']'

Giving us a rule for name based requirements::

    name_req      = name wsp* extras? wsp* versionspec? wsp* quoted_marker?

And a rule for direct reference specifications::

    url_req       = name wsp* extras? wsp* urlspec wsp+ quoted_marker?

Leading to the unified rule that can specify a dependency.::

    specification = wsp* ( url_req | name_req ) wsp*

Whitespace
----------

Non line-breaking whitespace is mostly optional with no semantic meaning. The
sole exception is detecting the end of a URL requirement.

Names
-----

Python distribution names are currently defined in PEP-345 [#pep345]_. Names
act as the primary identifier for distributions. They are present in all
dependency specifications, and are sufficient to be a specification on their
own. However, PyPI places strict restrictions on names - they must match a
case insensitive regex or they won't be accepted. Accordingly in this PEP we
limit the acceptable values for identifiers to that regex. A full redefinition
of name may take place in a future metadata PEP. The regex (run with
re.IGNORECASE) is::

    ^([A-Z0-9]|[A-Z0-9][A-Z0-9._-]*[A-Z0-9])$

Extras
------

An extra is an optional part of a distribution. Distributions can specify as
many extras as they wish, and each extra results in the declaration of
additional dependencies of the distribution **when** the extra is used in a
dependency specification. For instance::

    requests[security]

Extras union in the dependencies they define with the dependencies of the
distribution they are attached to. The example above would result in requests
being installed, and requests own dependencies, and also any dependencies that
are listed in the "security" extra of requests.

If multiple extras are listed, all the dependencies are unioned together.

Versions
--------

See PEP-440 [#pep440]_ for more detail on both version numbers and version
comparisons. Version specifications limit the versions of a distribution that
can be used. They only apply to distributions looked up by name, rather than
via a URL. Version comparison are also used in the markers feature. The
optional brackets around a version are present for compatibility with PEP-345
[#pep345]_ but should not be generated, only accepted.

Environment Markers
-------------------

Environment markers allow a dependency specification to provide a rule that
describes when the dependency should be used. For instance, consider a package
that needs argparse. In Python 2.7 argparse is always present. On older Python
versions it has to be installed as a dependency. This can be expressed as so::

    argparse;python_version<"2.7"

A marker expression evalutes to either True or False. When it evaluates to
False, the dependency specification should be ignored.

The marker language is inspired by Python itself, chosen for the ability to
safely evaluate it without running arbitrary code that could become a security
vulnerability. Markers were first standardised in PEP-345 [#pep345]_. This PEP
fixes some issues that were observed in the design described in PEP-426
[#pep426]_.

Comparisons in marker expressions are typed by the comparison operator.  The
<marker_op> operators that are not in <version_cmp> perform the same as they
do for strings in Python. The <version_cmp> operators use the PEP-440
[#pep440]_ version comparison rules when those are defined (that is when both
sides have a valid version specifier). If there is no defined PEP-440
behaviour and the operator exists in Python, then the operator falls back to
the Python behaviour. Otherwise an error should be raised. e.g. the following
will result in  errors::

    "dog" ~= "fred"
    python_version ~= "surprise"

User supplied constants are always encoded as strings with either ``'`` or
``"`` quote marks. Note that backslash escapes are not defined, but existing
implementations do support them. They are not included in this
specification because they add complexity and there is no observable need for
them today. Similarly we do not define non-ASCII character support: all the
runtime variables we are referencing are expected to be ASCII-only.

The variables in the marker grammar such as "os_name" resolve to values looked
up in the Python runtime. With the exception of "extra" all values are defined
on all Python versions today - it is an error in the implementation of markers
if a value is not defined.

Unknown variables must raise an error rather than resulting in a comparison
that evaluates to True or False.

Variables whose value cannot be calculated on a given Python implementation
should evaluate to ``0`` for versions, and an empty string for all other
variables.

The "extra" variable is special. It is used by wheels to signal which
specifications apply to a given extra in the wheel ``METADATA`` file, but
since the ``METADATA`` file is based on a draft version of PEP-426, there is
no current specification for this. Regardless, outside of a context where this
special handling is taking place, the "extra" variable should result in an
error like all other unknown variables.

.. list-table::
   :header-rows: 1

   * - Marker
     - Python equivalent
     - Sample values
   * - ``os_name``
     - ``os.name``
     - ``posix``, ``java``
   * - ``sys_platform``
     - ``sys.platform``
     - ``linux``, ``linux2``, ``darwin``, ``java1.8.0_51`` (note that "linux"
       is from Python3 and "linux2" from Python2)
   * - ``platform_machine``
     - ``platform.machine()``
     - ``x86_64``
   * - ``python_implementation``
     - ``platform.python_implementation()``
     - ``CPython``, ``Jython``
   * - ``platform_release``
     - ``platform.release()``
     - ``3.14.1-x86_64-linode39``, ``14.5.0``, ``1.8.0_51``
   * - ``platform_system``
     - ``platform.system()``
     - ``Linux``, ``Windows``, ``Java``
   * - ``platform_version``
     - ``platform.version()``
     - ``#1 SMP Fri Apr 25 13:07:35 EDT 2014``
       ``Java HotSpot(TM) 64-Bit Server VM, 25.51-b03, Oracle Corporation``
       ``Darwin Kernel Version 14.5.0: Wed Jul 29 02:18:53 PDT 2015; root:xnu-2782.40.9~2/RELEASE_X86_64``
   * - ``python_version``
     - ``platform.python_version()[:3]``
     - ``3.4``, ``2.7``
   * - ``python_full_version``
     - ``platform.python_version()``
     - ``3.4.0``, ``3.5.0b1``
   * - ``implementation_name``
     - ``sys.implementation.name``
     - ``cpython``
   * - ``implementation_version``
     - see definition below
     - ``3.4.0``, ``3.5.0b1``
   * - ``extra``
     - An error except when defined by the context interpreting the
       specification.
     - ``test``

The ``implementation_version`` marker variable is derived from
``sys.implementation.version``::

    def format_full_version(info):
        version = '{0.major}.{0.minor}.{0.micro}'.format(info)
        kind = info.releaselevel
        if kind != 'final':
            version += kind[0] + str(info.serial)
        return version

    if hasattr(sys, 'implementation'):
        implementation_version = format_full_version(sys.implementation.version)
    else:
        implementation_version = "0"

Backwards Compatibility
=======================

Most of this PEP is already widely deployed and thus offers no compatibility
concerns.

There are however a few points where the PEP differs from the deployed base.

Firstly, PEP-440 direct references haven't actually been deployed in the wild,
but they were designed to be compatibly added, and there are no known
obstacles to adding them to pip or other tools that consume the existing
dependency metadata in distributions - particularly since they won't be
permitted to be present in PyPI uploaded distributions anyway.

Secondly, PEP-426 markers which have had some reasonable deployment,
particularly in wheels and pip, will handle version comparisons with
``python_version`` "2.7.10" differently. Specifically in 426 "2.7.10" is less
than "2.7.9". This backward incompatibility is deliberate. We are also
defining new operators - "~=" and "===", and new variables -
``platform_release``, ``platform_system``, ``implementation_name``, and
``implementation_version`` which are not present in older marker
implementations. The variables will error on those implementations. Users of
both features will need to make a judgement as to when support has become
sufficiently widespread in the ecosystem that using them will not cause
compatibility issues.

Thirdly, PEP-345 required brackets around version specifiers. In order to
accept PEP-345 dependency specifications, brackets are accepted, but they
should not be generated.

Rationale
=========

In order to move forward with any new PEPs that depend on environment markers,
we needed a specification that included them in their modern form. This PEP
brings together all the currently unspecified components into a specified
form.

The requirement specifier was adopted from the EBNF in the setuptools
pkg_resources documentation, since we wish to avoid depending on a defacto, vs
PEP specified, standard.

Complete Grammar
================

The complete parsley grammar::

    wsp           = ' ' | '\t'
    version_cmp   = wsp* <'<' | '<=' | '!=' | '==' | '>=' | '>' | '~=' | '==='>
    version       = wsp* <( letterOrDigit | '-' | '_' | '.' | '*' | '+' | '!' )+>
    version_one   = version_cmp:op version:v wsp* -> (op, v)
    version_many  = version_one:v1 (wsp* ',' version_one)*:v2 -> [v1] + v2
    versionspec   = ('(' version_many:v ')' ->v) | version_many
    urlspec       = '@' wsp* <URI_reference>
    marker_op     = version_cmp | (wsp* 'in') | (wsp* 'not' wsp+ 'in')
    python_str_c  = (wsp | letter | digit | '(' | ')' | '.' | '{' | '}' |
                     '-' | '_' | '*' | '#' | ':' | ';' | ',' | '/' | '?' |
                     '[' | ']' | '!' | '~' | '`' | '@' | '$' | '%' | '^' |
                     '&' | '=' | '+' | '|' | '<' | '>' )
    dquote        = '"'
    squote        = '\\''
    python_str    = (squote <(python_str_c | dquote)*>:s squote |
                     dquote <(python_str_c | squote)*>:s dquote) -> s
    env_var       = ('python_version' | 'python_full_version' |
                     'os_name' | 'sys_platform' | 'platform_release' |
                     'platform_system' | 'platform_version' |
                     'platform_machine' | 'python_implementation' |
                     'implementation_name' | 'implementation_version' |
                     'extra' # ONLY when defined by a containing layer
                     ):varname -> lookup(varname)
    marker_var    = wsp* (env_var | python_str)
    marker_expr   = marker_var:l marker_op:o marker_var:r -> (o, l, r)
                  | wsp* '(' marker:m wsp* ')' -> m
    marker_and    = marker_expr:l wsp* 'and' marker_expr:r -> ('and', l, r)
                  | marker_expr:m -> m
    marker_or     = marker_and:l wsp* 'or' marker_and:r -> ('or', l, r)
                      | marker_and:m -> m
    marker        = marker_or
    quoted_marker = ';' wsp* marker
    identifier    = <letterOrDigit (
                    letterOrDigit |
                    (( letterOrDigit | '-' | '_' | '.')* letterOrDigit ) )*>
    name          = identifier
    extras_list   = identifier:i (wsp* ',' wsp* identifier)*:ids -> [i] + ids
    extras        = '[' wsp* extras_list?:e wsp* ']' -> e
    name_req      = (name:n wsp* extras?:e wsp* versionspec?:v wsp* quoted_marker?:m
                     -> (n, e or [], v or [], m))
    url_req       = (name:n wsp* extras?:e wsp* urlspec:v wsp+ quoted_marker?:m
                     -> (n, e or [], v, m))
    specification = wsp* ( url_req | name_req ):s wsp* -> s
    # The result is a tuple - name, list-of-extras,
    # list-of-version-constraints-or-a-url, marker-ast or None


    URI_reference = <URI | relative_ref>
    URI           = scheme ':' hier_part ('?' query )? ( '#' fragment)?
    hier_part     = ('//' authority path_abempty) | path_absolute | path_rootless | path_empty
    absolute_URI  = scheme ':' hier_part ( '?' query )?
    relative_ref  = relative_part ( '?' query )? ( '#' fragment )?
    relative_part = '//' authority path_abempty | path_absolute | path_noscheme | path_empty
    scheme        = letter ( letter | digit | '+' | '-' | '.')*
    authority     = ( userinfo '@' )? host ( ':' port )?
    userinfo      = ( unreserved | pct_encoded | sub_delims | ':')*
    host          = IP_literal | IPv4address | reg_name
    port          = digit*
    IP_literal    = '[' ( IPv6address | IPvFuture) ']'
    IPvFuture     = 'v' hexdig+ '.' ( unreserved | sub_delims | ':')+
    IPv6address   = (
                      ( h16 ':'){6} ls32
                      | '::' ( h16 ':'){5} ls32
                      | ( h16 )?  '::' ( h16 ':'){4} ls32
                      | ( ( h16 ':')? h16 )? '::' ( h16 ':'){3} ls32
                      | ( ( h16 ':'){0,2} h16 )? '::' ( h16 ':'){2} ls32
                      | ( ( h16 ':'){0,3} h16 )? '::' h16 ':' ls32
                      | ( ( h16 ':'){0,4} h16 )? '::' ls32
                      | ( ( h16 ':'){0,5} h16 )? '::' h16
                      | ( ( h16 ':'){0,6} h16 )? '::' )
    h16           = hexdig{1,4}
    ls32          = ( h16 ':' h16) | IPv4address
    IPv4address   = dec_octet '.' dec_octet '.' dec_octet '.' Dec_octet
    nz            = ~'0' digit
    dec_octet     = (
                      digit # 0-9
                      | nz digit # 10-99
                      | '1' digit{2} # 100-199
                      | '2' ('0' | '1' | '2' | '3' | '4') digit # 200-249
                      | '25' ('0' | '1' | '2' | '3' | '4' | '5') )# %250-255
    reg_name = ( unreserved | pct_encoded | sub_delims)*
    path = (
            path_abempty # begins with '/' or is empty
            | path_absolute # begins with '/' but not '//'
            | path_noscheme # begins with a non-colon segment
            | path_rootless # begins with a segment
            | path_empty ) # zero characters
    path_abempty  = ( '/' segment)*
    path_absolute = '/' ( segment_nz ( '/' segment)* )?
    path_noscheme = segment_nz_nc ( '/' segment)*
    path_rootless = segment_nz ( '/' segment)*
    path_empty    = pchar{0}
    segment       = pchar*
    segment_nz    = pchar+
    segment_nz_nc = ( unreserved | pct_encoded | sub_delims | '@')+
                    # non-zero-length segment without any colon ':'
    pchar         = unreserved | pct_encoded | sub_delims | ':' | '@'
    query         = ( pchar | '/' | '?')*
    fragment      = ( pchar | '/' | '?')*
    pct_encoded   = '%' hexdig
    unreserved    = letter | digit | '-' | '.' | '_' | '~'
    reserved      = gen_delims | sub_delims
    gen_delims    = ':' | '/' | '?' | '#' | '(' | ')?' | '@'
    sub_delims    = '!' | '$' | '&' | '\\'' | '(' | ')' | '*' | '+' | ',' | ';' | '='
    hexdig        = digit | 'a' | 'A' | 'b' | 'B' | 'c' | 'C' | 'd' | 'D' | 'e' | 'E' | 'f' | 'F'

A test program - if the grammar is in a string ``grammar``::

    import os
    import sys
    import platform

    from parsley import makeGrammar

    grammar = """
        wsp ...
        """
    tests = [
        "A",
        "aa",
        "name",
        "name>=3",
        "name>=3,<2",
        "name [fred,bar] @ http://foo.com ; python_version=='2.7'",
        "name[quux, strange];python_version<'2.7' and platform_version=='2'",
        "name; os_name=='a' or os_name=='b'",
        # Should parse as (a and b) or c
        "name; os_name=='a' and os_name=='b' or os_name=='c'",
        # Overriding precedence -> a and (b or c)
        "name; os_name=='a' and (os_name=='b' or os_name=='c')",
        # should parse as a or (b and c)
        "name; os_name=='a' or os_name=='b' and os_name=='c'",
        # Overriding precedence -> (a or b) and c
        "name; (os_name=='a' or os_name=='b') and os_name=='c'",
        ]

    def format_full_version(info):
        version = '{0.major}.{0.minor}.{0.micro}'.format(info)
        kind = info.releaselevel
        if kind != 'final':
            version += kind[0] + str(info.serial)
        return version

    if hasattr(sys, 'implementation'):
        implementation_version = format_full_version(sys.implementation.version)
        implementation_name = sys.implementation.name
    else:
        implementation_version = '0'
        implementation_name = ''
    bindings = {
        'implementation_name': implementation_name,
        'implementation_version': implementation_version,
        'os_name': os.name,
        'platform_machine': platform.machine(),
        'platform_release': platform.release(),
        'platform_system': platform.system(),
        'platform_version': platform.version(),
        'python_full_version': platform.python_version(),
        'python_implementation': platform.python_implementation(),
        'python_version': platform.python_version()[:3],
        'sys_platform': sys.platform,
    }

    compiled = makeGrammar(grammar, {'lookup': bindings.__getitem__})
    for test in tests:
        parsed = compiled(test).specification()
        print("%s -> %s" % (test, parsed))

References
==========

.. [#pip] pip, the recommended installer for Python packages
   (http://pip.readthedocs.org/en/stable/)

.. [#pep345] PEP-345, Python distribution metadata version 1.2.
   (https://www.python.org/dev/peps/pep-0345/)

.. [#pep426] PEP-426, Python distribution metadata.
   (https://www.python.org/dev/peps/pep-0426/)

.. [#pep440] PEP-440, Python distribution metadata.
   (https://www.python.org/dev/peps/pep-0440/)

.. [#std66] The URL specification.
   (https://tools.ietf.org/html/rfc3986)

.. [#parsley] The parsley PEG library.
   (https://pypi.python.org/pypi/parsley/)

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
