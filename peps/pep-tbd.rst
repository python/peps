PEP: tbd
Title: Emscripten Packaging
Author: Hood Chatham <roberthoodchatham at gmail.com>
Sponsor: Łukasz Langa <lukasz at python.org>
Discussions-To: 
Status: Draft
Type: Standards Track
Topic: Packaging
Created: 28-Mar-2025
Post-History: 

Abstract
========

This PEP proposes a new platform tag series `pyodide` for binary Python package
distributions for the Pyodide Python runtime.

`Emscripten <https://emscripten.org/>`__ is a complete open source compiler
toolchain. It compiles C/C++ code into WebAssembly/JavaScript executables, for
use in JavaScript runtimes, including browsers and Node.js. The Rust language
also maintains an Emscripten target.

The goals of this PEP are:

1. To describe Pyodide's packaging tooling
2. To describe Pyodide's wheel abi to a similar level of detail as the manylinux
   PEPs
3. For Pyodide wheels to be allowed for upload to PyPI



Motivation
==========

Pyodide is a CPython distribution for use in the browser. A web browser is a
universal computing platform, available on Windows, macOS, Linux, and every
smartphone. Hundreds of thousands of students have learned Python through
Pyodide via projects like `Capytale
<https://web.archive.org/web/20241211090946/https://cfp.jupytercon.com/2023/talk/TJ9YEV/>`__
and `PyodideU <https://stanford.edu/~cpiech/bio/papers/pyodideU.pdf>`__. Pyodide
is also increasingly being used by Python packages to provide interactive
documentation.

Pyodide currently maintains ports of 255 different packages at the time of this
writing, including major scientific Python packages like NumPy, SciPy, pandas,
Polars, scikit-learn, OpenCV, PyArrow, and Pillow as well as general purpose
packages like aiohttp, Requests, Pydantic, cryptography, and orjson.

About 60 packages are also testing against Pyodide in their CI, including NumPy,
pandas, awkward-cpp, scikit-image, statsmodels, PyArrow, Hypothesis, and PyO3.

Python package projects cannot deploy binary distributions for Pyodide on PyPI.
Instead they must use other options like ``anaconda.org`` or ``jsdelivr.com``.
This creates friction both for package maintainers and for users.


Rationale
=========

Emscripten uses a variant of musl libc. The Emscripten compiler makes no ABI
stability guarantees between versions. Many Emscripten updates are ABI
compatible by chance, and the Rust Emscripten target behaves as if the ABI were
stable with only `occasional negative consequences
<https://github.com/rust-lang/rust/issues/131467>`__.

There are several linker flags that adjust the Emscripten ABI, so Python
packages built to run with Emscripten must make sure to match the ABI-sensitive
linker flags used to compile the interpreter to avoid load-time or run-time
errors. The Emscripten compiler continuously fixes bugs and adds support for new
web platform features. Thus, there is significant benefit to being able to
update the ABI.

In order to balance the ABI stability needs of package maintainers with the ABI
flexibility to allow the platform to move forward, Pyodide plans to adopt a new
ABI for each feature release of Python.

The Pyodide team also coordinates the ABI flags that Pyodide uses with the
Emscripten ABI that Rust supports in order to ensure that we have support for
the many popular Rust packages. Historically, most of the work for this has
been related to unwinding ABIs. See for instance `this Rust Major Change
Proposal <https://github.com/rust-lang/compiler-team/issues/801>`__.

The ``pyodide`` platform tags only apply to Python interpreters compiled and
linked with the same version of Emscripten as Pyodide, with the same
ABI-sensitive flags.


Specification
=============

The platform tags will take the form::

    pyodide_${YEAR}_${PATCH}_wasm32

Each one of these will be used with a specified Python version. For example, the
platform tag `pyodide_2025_0` will be used with Python 3.13. 

Emscripten Wheel ABI
--------------------

The specification of the ``pyodide_<abi>`` platform includes:

* Which version of the Emscripten compiler is used
* What libraries are statically linked with the interpreter
* What stack unwinding ABI is to be used
* Which runtime platform features are required to be present

and a handful of other similar details that affect the ABI.

The ABI is selected by choosing the appropriate version of the Emscripten
compiler and passing appropriate compiler and linker flags. It is possible for
other people to build their own Python interpreter that is compatible with the
Pyodide ABI, it is not necessary to use the Pyodide distribution itself.

The ``pyodide build`` tool knows how to create wheels that match our ABI. Unlike
with manylinux wheels, there is no need for a Docker container to build the
``pyodide_<abi>`` wheels. All that is needed is a Linux machine and appropriate
versions of Python, Node.js, and Emscripten.

It is possible to validate a wheel by installing and importing it into the
Pyodide runtime. Because Pyodide can run in an environment with strong
sandboxing guarantees, doing this produces no security risks.

Determining the ABI version
---------------------------

The Pyodide ABI version is stored in the `PYODIDE_ABI_VERSION` config variable
and can be determined via::

    pyodide_abi_version = sysconfig.get_config_var("PYODIDE_ABI_VERSION")


To generate the list of compatible tags, one can use the following code::

    from packaging.tags import cpython_tags, _generic_platforms

    def _emscripten_platforms() -> Iterator[str]:
        pyodide_abi_version = sysconfig.get_config_var("PYODIDE_ABI_VERSION")
        if pyodide_abi_version:
            yield f"pyodide_{pyodide_abi_version}_wasm32"
        yield from _generic_platforms()

    emscripten_tags = cpython_tags(platforms=_emscripten_platforms())

This code will be added to `pypa/packaging
<https://github.com/pypa/packaging/pull/804>`__.


Package Installers
------------------

Installers should use the ``_emscripten_platforms()`` function shown above to
determine which platforms are compatible with an Emscripten build of CPython. In
particular, the Pyodide ABI version is exposed via
``sysconfig.get_config_var("PYODIDE_ABI_VERSION")``.

Package indexes
---------------

We recommend that package indexes accept any wheel whose platform tag matches
``pyodide_[0-9]+_[0-9]+_wasm32``.


Dependency Specifier Markers
----------------------------

To check for the Emscripten platform in a dependency specifier, one can use
``sys_platform == 'emscripten'`` (or its negation).


Trove Classifier
----------------

Packages that build and test Emscripten wheels can declare this by adding the
``Environment :: WebAssembly :: Emscripten``. PyPI already accepts uploads of
packages with this classifier.


Backwards Compatibility
=======================

There are no backwards compatibility concerns in this PEP.


Copyright
=========

This document is placed in the public domain or under the
CC0-1.0-Universal license, whichever is more permissive.
