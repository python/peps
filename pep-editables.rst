PEP: editables
Title: Editable installs for PEP-517 style build backends
Author: Daniel Holth <dholth@fastmail.fm>
Status: Draft
Content-Type: text/x-rst
Created: 30-Mar-2021
Post-History: 


Abstract
========

This document describes a PEP 517 style method for the installation of packages
in editable mode.

Motivation
==========

Python programmers want to be able to develop packages without having to
install (i.e. copy) them into ``site-packages``, for example, by working in a
checkout of the source repository.

While this can be done by adding the relevant source directories to
``PYTHONPATH``, ``setuptools`` provides the ``setup.py develop`` mechanism that
makes the process easier, and also installs dependencies and entry points such
as console scripts. ``pip`` exposes this mechanism via its ``pip install
--editable`` option.

The installation of projects in such a way that the python code being
imported remains in the source directory is known as the *editable*
installation mode.

Now that PEP 517 provides a mechanism to create alternatives to setuptools, and
decouple installation front ends from build backends, we need a new mechanism
to install packages in editable mode.

Rationale
=========

PEP 517 deferred "Editable installs", meaning non-``setup.py``
distributions lacked that feature. The only way to retain ``editable`` installs
for these distributions was to provide a compatible ``setup.py develop``
implementation. By definining an editable hook other build frontends gain
parity with ``setup.py``.

Terminology and goals
=====================

The editable installation mode implies that the source code of the project
being installed is available in a local directory.

Once the project is installed in editable mode, users expect that changes to
the project *python* code in the local source tree become effective without the
need of a new installation step.

Some kind of changes, such as the addition or modification of entry points, or
the addition of new dependencies, require a new installation step to become
effective. These changes are typically made in build backend configuration
files (such as ``pyproject.toml``), so it is consistent with the general user
expectation that *python* source code is imported from the source tree.

The modification of non-python source code such a C extension modules obviously
require a compilation and/or installation step to become effective. The exact
steps to perform will remain specific to the build backend used.

When a project is installed in editable mode, users expect the installation to
behave identically as a regular installation. Depending on the way build
backend implement this specification, some minor differences may be visible
such as the presence of additional files that are in the source tree and would
not be part of a regular install. Build backends are encouraged to document
such potential differences.

The Mechanism
=============

This PEP adds a single optional hook to the PEP-517 backend interface. The hook
is used to build a wheel that, when installed, allows that distribution to be
imported from its source folder. 

build_wheel_for_editable
------------------------

:: 

  def build_wheel_for_editable(
      wheel_directory,
      scheme=scheme, 
      metadata_directory=metadata_directory,
      config_settings=None):
      ...

``scheme``: a dictionary of installation categories ``{ 'purelib':
'/home/py/.../site-packages', 'platlib': '...'}``. This makes it possible to
use relative paths to the source code, which might help the interpreter find
the package after the root path changes with ``chroot`` or similar.

Must build a ``.whl`` file, and place it in the specified ``wheel_directory``.
It must return the basename (not the full path) of the .whl file it creates, as
a unicode string.

May do an in-place build of the distribution as a side effect so that any
extension modules or other built artifacts are ready to be used.

The .whl file must comply with the Wheel binary file format specification (PEP
427). In particular it must contain a compliant .dist-info directory. The
metadata may differ from what ``build_wheel`` produces, although the
differences are expected to be minimal to remain compatible with the goals of
editable installs described above.

In particular the ``Version`` metadata may differ, and build-backends are
encouraged to append a distinguishable PEP 440 *local version identifier*, such
as ``+editable``, so as to make editable installs easier to identify by users
inspecting installed distributions. Since public index servers reject wheels
containing local version identifiers, this approach has the interesting
property of preventing accidental publishing of editable wheels.

The filename for the “editable” wheel need not use the same tags as
``build_wheel`` but must be tagged as compatible with the system.

If the build frontend has previously called
``prepare_metadata_for_build_wheel`` and depends on the wheel resulting from
this call to have metadata matching this earlier call, then it should provide
the path to the created .dist-info directory as the metadata_directory
argument.

Backends which do not provide the ``prepare_metadata_for_build_wheel`` hook may
either silently ignore the metadata_directory parameter to
build_wheel_for_editable, or else raise an exception when it is set to anything
other than None.

An “editable” wheel uses the wheel format not for distribution but as ephemeral
communication between the build system and the front end. This avoids having
the build backend install anything directly, but these wheels should not be
cached or distributed.

What to put in the wheel
------------------------

Build backends may use different techniques to achive the goals of an editable
install. This section provides examples and is not normative.

* Build backends may chose to place a ``.pth`` file at the root of the ``.whl`` file,
  containing the root directory of the source tree. This approach is simple but
  not very precise, although it may be considered good enough (especially when
  using the ``src`` layout) and is similar to what ``setup.py develop``
  currently does.
* The `editables`_ library shows how to build proxy modules that
  provide a high quality editable installation. It accepts a list of modules
  to include, and hide. When imported, these proxy modules replace themselves
  with the code from the source tree. Path-based methods make all scripts under
  a path importable, often including the project's own ``setup.py`` and other
  scripts that would not be part of a normal installation. The proxy strategy
  can achieve a higher level of fidelity than path-based methods.

Frontend requirements
---------------------

Frontends must handle the ``metadata_directory`` of
``build_wheel_for_editable`` argument in the same way as the one of
``build_wheel``.

Frontends must install editable wheels in the same way as regular wheels.

Frontends must create a ``direct_url.json`` file in the ``.dist-info``
directory of the installed distribution, in compliance with PEP 610. The
``url`` value must be a ``file://`` url pointing to the project directory
(i.e. the directory containing ``pyproject.toml``), and the ``dir_info`` value
must be ``{'editable': true}``.

References
==========

.. _`editables`: https://pypi.org/project/editables/

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
