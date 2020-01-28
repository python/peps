PEP: 9999
Title: Disabling Manylinux
Version: $Revision$
Last-Modified: $Date$
Author: James Tocknell <aragilar@gmail.com>
Status: Draft
Type: Informational
Content-Type: text/x-rst
Created: 2020-01-28
Python-Version: [M.N]
Created: 2020-01-28
Resolution:

Abstract and Motivation
=======================

Manylinux has been successful in allowing users to install non-pure-python
python packages, without the need of a compiler (or compliers) or the need to
install other shared libraries. This has increased usability of the python
packaging ecosystem, and reduced time waiting on CI builds. However, manylinux
has increased the issues some users face, therefore these users wish to opt out
of using manylinux wheels. They may be encountering issues with projects
producing invalid manylinux wheels [#manylinux-tensorflow], wanting to
experiment with different BLAS/LAPACK implementations, or a variety of other
reasons [#pip-no-manylinux]. Currently, the only way of overriding is to put
specific text strings in a `_manylinux.py` file. This has proven to not be
future-proof [#packaging-pip-issue], and, due to the reliance of a specific
ordering of the python path, there is currently no option for users to have the
install of manylinux wheels fail closed.


Specification
=============

Implementers of this PEP should check for the presence of an environmental
variable `PYTHON_NO_MANYLINUX`, and then check the truthyness of
`_manylinux.no_manylinux`, before applying any other manylinux compatibility
logic. The following example code should be sufficient for implementing this::

    if os.environ.get("PYTHON_NO_MANYLINUX"):
        return False
    try:
        import _manylinux
    except ImportError:
        # No _manylinux module, use logic as outlined in other PEPs.
        pass
    else:
        if not getattr(_manylinux, "no_manylinux", True):
            return False


Rationale and Backwards Compatibility
=====================================

The use of both an environment variable, and another line in `_manylinux` allows
for as minimal as possible changes to existing user setups, allowing the
following contents of `_manylinux` to work across all installers which have
manylinux support::

    manylinux1_compatible = False
    manylinux2010_compatible = False
    manylinux2014_compatible = False
    no_manylinux = True

With PEP 600 [#pep600] using the version of glibc as the identifier for
compatibility, with control via a `_manylinux.manylinux_compatible` function,
the environment variable thereby avoids the conflict between the distributor
indicating levels of support and the user who wishes to disable the use of
manylinux wheels.


Security Implications
=====================

While some users have stated the use of vendored binaries as a security issue
for them, this PEP does not have an opinion either way, and is not interested in
determining the level of security associated with using manylinux wheels.
Running code from PyPI (whether a manylinux wheel, the setup.py inside a sdist,
or even a pure python wheel) is a decision of its users, and the exact form the
code takes is unlikely to change the threat level of the code.


Reference Implementation
========================

The is an existing PR on the packaging project GitHub tracker [#ghpr].


Rejected Ideas
==============

There is an issue [#pip-no-manylinux] on the pip issue tracker on GitHub
requesting some kind command line support for avoiding installing manylinux
wheels, however there is no agreement about what the exact interface should be.
Additionally, having a installer independent way of disabling manylinux means
that users can be more sure that their setup will fail closed when rejecting
manylinux wheels.


References
==========

.. [#manylinux-tensorflow] Tensorflow produced wheels that weren't compliant
    with the manylinux specification, see
    https://github.com/tensorflow/tensorflow/issues/8802
.. [#ghpr] https://github.com/pypa/packaging/pull/262
.. [#pip-no-manylinux] https://github.com/pypa/pip/issues/3689 is an issue on
    the pip issue tracker requesting that pip provide some way of opting out of
    using manylinux wheels, with some additional use cases mentioned.
.. [#packaging-pip-issue] https://github.com/pypa/pip/issues/7648 was the
    motivating issue which started the creation of this PEP.


Copyright
=========

This document is placed in the public domain or under the
CC0-1.0-Universal license, whichever is more permissive.



..
   Local Variables:
   mode: indented-text
   indent-tabs-mode: nil
   sentence-end-double-space: t
   fill-column: 70
   coding: utf-8
   End:
