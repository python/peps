PEP: 9999
Title: Specifying external dependencies in pyproject.toml
Author: Pradyun Gedam <pradyunsg@gmail.com>,
        Ralf Gommers <ralf.gommers@gmail.com
Discussions-To: https://discuss.python.org/t/TODO
Status: Draft
Type: Standards Track
Topic: Packaging
Content-Type: text/x-rst
Created: 16-Feb-2023
Post-History: 16-Feb-2023,
Resolution:


.. canonical-pypa-spec:: :ref:`packaging:declaring-external-dependencies`


Abstract
========

This PEP specifies how to write a project's external, or non-PyPI, build and
runtime dependencies in a ``pyproject.toml`` file for packaging-related tools
to consume.

TODO: does `core metadata`_ need to be extended with these dependencies?
@Pradyun would you be able to add the core metadata related content - I'm not
very familiar with it.


Motivation
==========

Python packages may have dependencies on build tools, libraries, command line
tools, or other software that is not present on PyPI. Currently there is no way
to express those dependencies in standardized metadata. Key motivators for
this PEP are:

- Enable tools to automatically map external dependencies to packages in other
  packaging repositories,
- Make it possible to include needed dependencies in error messages emitting by
  Python package installers and build frontends,
- Provide a canonical place for package authors to record this dependency
  information.

Packaging ecosystems like Linux distros, Conda, Homebrew, Spack, and Nix need
full sets of dependencies for Python packages, and have tools like pyp2rpm_
(Fedora), Grayskull_ (Conda), and dh_python_ (Debian) which attempt to
automatically generate dependency metadata automatically from the metadata in
upstream Python packages. External dependencies are currently handled manually,
because there is no metadata for this in ``pyproject.toml`` or any other
standard metadata file. Enabling automating this conversion is a key benefit of
this PEP, making packaging Python easier and more reliable. In addition, the
authors envision other types of tools making use of this information, e.g.,
dependency analysis tools like Dependabot_ and libraries.io_.

Packages with external dependencies are typically hard to build from source,
and error messages from build failures tend to be hard to decipher for end
users. Missing external dependencies on the end users system are the most
likely cause of build failures. If installers can show the required external
dependencies as part of their error message, this may save users a lot of time.

At the moment, information on external dependencies is only captured in
installation documentation of individual packages. It is hard to maintain for
package authors and tends to go out of date. It's also hard for users and
distro packagers to find it. Having a canonical place to record this dependency
information will improve this situation.

This PEP is not trying to specify how the external dependencies should be used,
nor a mechanism to implement a name mapping from names of individual packages
that are canonical for Python projects published on PyPI to those of other
packaging ecosystems. Those topics should be treated in separate PEPs which may
lead to changes or additions to what this PEP specifies.

*TODO: decide if we write a parallel PEP for the name mapping mechanism now, or
fold it into this PEP after all.*


Rationale
=========


Types of external dependencies
------------------------------

Multiple types of external dependencies can be distinguished:

- Concrete packages that can be identified by name and have a canonical
  location in another language-specific package repository. E.g., Rust
  packages on `crates.io <https://crates.io/>`__, R packages on
  `CRAN <https://cran.r-project.org/`__, JavaScript packages on the
  `npm registry <https://www.npmjs.com/>`__.
- Concrete packages that can be identified by name but do not have a clear
  canonical location. This is typically the case for libraries and tools
  written in C, C++, Fortran, CUDA and other low-level languages. E.g.,
  Boost, OpenSSL, Protobuf, Intel MKL, GCC.
- "Virtual" packages, which are names for concepts, types of tools or
  interfaces. These typically have multiple implementations, which *are*
  concrete packages. E.g., a C++ compiler, SSL, BLAS, LAPACK, OpenMP, MPI.

*TODO: PURL supports VCS links like pkg://github - should we allow that for
packages without a release? What about pkg://generic? I think generic is better
that github.*

Concrete packages are straightforward to understand, and are a concept present
in virtually every package management system. Virtual packages are a concept
also present in a number of packaging systems - but not always, and the details
of their implementation varies. 

Specifying external dependencies
--------------------------------

Concrete package specification through PURL
'''''''''''''''''''''''''''''''''''''''''''

The two types of concrete packages are supported by PURL_ (Package URL), which
implements a scheme for identifying packages that is meant to be portable
across packaging ecosystems. Its design is::

    scheme:type/namespace/name@version?qualifiers#subpath 

The ``scheme`` component is a fixed string, ``pkg``, and of the other
components only ``type`` and ``name`` are required. As an example, a package
URL for the ``requests`` package on PyPI would be::

    pkg:pypi/requests

Adopting PURL to specify external dependencies in ``pyproject.toml`` solves a
number of problems at once - and there are already implementations of the
specification in Python and multiple languages. PURL is also already supported
by dependency-related tooling like SPDX (see
`External Repository Identifiers in the SPDX 2.3 spec <https://spdx.github.io/spdx-spec/v2.3/external-repository-identifiers/#f35-purl>`__),
the `Open Source Vulnerability format <https://ossf.github.io/osv-schema/#affectedpackage-field>`__,
and the `Sonatype OSS Index <https://ossindex.sonatype.org/doc/coordinates>`__;
not having to wait years before support in such tooling arrives is valuable.

Virtual package specification
'''''''''''''''''''''''''''''

There is no ready-made support for virtual packages in PURL or another
standard. There are a relatively limited number of such dependencies though,
and adoption a scheme similar to PURL but with the ``virtual:`` rather than
``pkg:`` scheme seems like it will be understandable and map well to Linux
distros with virtual packages and the likes of Conda and Spack.

Versioning
''''''''''

Support in PURL for version expresses and ranges is still pending, see
`vers implementation for PURL`_. In the absence of that support, the authors of
this PEP choose to not support versioning for external dependencies yet.


Dependency specifiers
'''''''''''''''''''''

*TODO: do we allow dependency specifier like ``; platform_system=='Linux'`
behind PURLs? Gut feel: no.*


Specification
=============

If metadata is improperly specified then tools MUST raise an error to notify
the user about their mistake.


Details
-------

.. note::

   ``pyproject.toml`` content is in the same format as in :pep:`621`

Table name
''''''''''

Tools MUST specify fields defined by this PEP in a table named
``[external-dependencies]``. No tools may add fields to this table which are
not defined by this PEP or subsequent PEPs.
The lack of an ``[external-dependencies]`` table means the package either does
not have any external dependencies, or the ones it does have are assumed to be
present on the system already.

``build-requires``/``optional-build-requires``
''''''''''''''''''''''''''''''''''''''''''''''

- Format: Array of PURL_ strings (``dependencies``) and a table
  with values of arrays of PURL_ strings (``optional-dependencies``)
- `Core metadata`_: TODO

``dependencies``/``optional-dependencies``
''''''''''''''''''''''''''''''''''''''''''
- Format: Array of PURL_ strings (``dependencies``) and a table
  with values of arrays of PURL_ strings (``optional-dependencies``)
- `Core metadata`_: TODO

The (optional) dependencies of the project.

For ``dependencies``, it is a key whose value is an array of strings.
Each string represents a dependency of the project and MUST be
formatted as either a valid PURL_ string or a ``virtual:`` string. Each string
maps directly to a ``TODO`` entry in the `core metadata`_.

For ``optional-dependencies``, it is a table where each key specifies
an extra and whose value is an array of strings. The strings of the
arrays must be valid PURL_ strings. The keys MUST be valid values
for the ``TODO`` `core metadata`_. Each value in the array
thus becomes a corresponding ``TODO`` entry for the matching
``TODO`` metadata.


Example
-------

*TODO: should we get this right at once for cross-compiling?* E.g., conda-forge
uses ``build``, ``host`` and ``run`` keys; for non-cross-compiling jobs
``host`` dependencies equal ``build`` dependencies. Spack has this too, in a
similar form: dependencies have a keyword ``type`` which can be a string or
tuple of strings - "build", "link", "run". ``type="build"`` are build systems
and code generators, a header-only library like ``pybind11`` is ``("build",
"link")`` while the likes of python and numpy are ``("build", "link", "run")``.


cryptography:

.. code:: toml

    [external-dependencies]
    build-requires = [
      "virtual:compiler{'rust'}",  # TODO: syntax? `compiler-c`, or ...?
      "virtual:ssl",
    ]

SciPy:

.. code:: toml

    [external-dependencies]
    build-requires = [
      "virtual:compiler{'c'}",
      "virtual:compiler{'c++'}",
      "virtual:compiler{'fortran'}",
      "virtual:blas",
      "virtual:lapack>=3.7.1",
      "pkg:generic/ninja",
    ]

    optional-build-requires = [
      "pkg:generic/pkg-config",
      "pkg:generic/cmake",
    ]

pygraphviz:

.. code:: toml

    [external-dependencies]
    build-requires = [
      "virtual:compiler{'c'}",
      "pkg:generic/graphviz",
    ]

*TODO: for packages that are build dependencies to link against, like graphviz,
openssl or OpenBLAS, is there a need to list them also as runtime dependencies?
Probably not, seems obvious - it seems like the packaging system should get
this right automatically.*

NAVis:

.. code:: toml

    [project]
    optional-dependencies = "rpy2"

    [external-dependencies]
    build-requires = [
      "pkg:generic/XCB; platform_system=='Linux'",
    ]

    optional-dependencies = [
      "pkg:cran/nat",
      "pkg:cran/nat.nblast",
    ]

jupyterlab-git:

.. code:: toml

    [external-dependencies]
    build-requires = [
      "pkg:generic/nodejs",
    ]
    dependencies = [
      "pkg:generic/git",
    ]

*TODO: jupyterlab-git has many JS dependencies (see
https://github.com/jupyterlab/jupyterlab-git/blob/master/package.json), but
it's not clear whether it's desirable to list all those as external
dependencies. Technically yes, but pragmatically .... not sure. JS packages are
a bit special, because they're so granular."*


Backwards Compatibility
=======================

There is no impact on backwards compatibility, as this PEP only adds new,
optional metadata. In the absence of such metadata, nothing changes for package
authors or packaging tooling.


Security Implications
=====================

There are no direct security concerns as this PEP covers how to statically
define metadata for external depedencies. Any security issues would stem from
how tools consume the metadata and choose to act upon it.


How to Teach This
=================

TODO


Reference Implementation
========================


Rejected Ideas
==============

Specific syntax for external dependencies which are also packaged on PyPI
-------------------------------------------------------------------------

There are non-Python packages which are packaged on PyPI, such as Ninja,
patchelf and CMake. What is typically desired is to use the system version of
those, and if it's not present on the system then install the PyPI package for
it. The authors believe that specific support for this scenario is not
necessary (or too complex to justify such support); a dependency provider for
external dependencies can treat PyPI as one possible source for obtaining the
package.

Using library and header names as external dependencies
-------------------------------------------------------

A previous draft PEP (`"External dependencies (2015) <https://github.com/pypa/interoperability-peps/pull/30>`__)
proposed using specific library and header names as external dependencies. This
is too granular; using package names is a well-established pattern across
packaging ecosystems and should be preferred.


Open Issues
===========
None at the moment.


Copyright
=========

This document is placed in the public domain or under the
CC0-1.0-Universal license, whichever is more permissive.


.. _PyPI: https://pypi.org
.. _core metadata: https://packaging.python.org/specifications/core-metadata/
.. _setuptools: https://setuptools.readthedocs.io/
.. _setuptools metadata: https://setuptools.readthedocs.io/en/latest/setuptools.html#metadata
.. _SPDX: https://spdx.dev/
.. _PURL: https://github.com/package-url/purl-spec/
.. _vers: https://github.com/package-url/purl-spec/blob/version-range-spec/VERSION-RANGE-SPEC.rst
.. _vers implementation for PURL: https://github.com/package-url/purl-spec/pull/139
.. _pyp2rpm: https://github.com/fedora-python/pyp2rpm
.. _Grayskull: https://github.com/conda/grayskull
.. _dh_python: https://www.debian.org/doc/packaging-manuals/python-policy/index.html#dh-python
.. _Dependabot: https://github.com/dependabot
.. _libraries.io: https://libraries.io/


..
   Local Variables:
   mode: indented-text
   indent-tabs-mode: nil
   sentence-end-double-space: t
   fill-column: 70
   coding: utf-8
   End:
