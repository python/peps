PEP: editables
Title: Editable installs for PEP-517 style build backends
Author: Daniel Holth <dholth@fastmail.fm>
Status: Draft
Content-Type: text/x-rst
Created: 30-Mar-2021
Post-History: 


Abstract
========

Python programmers want to be able to develop packages without
having to install them into ``site-packages``, for example, by editing
a checkout of the source repository. First ``PYTHONPATH`` or 
``.pth`` files added the source directory to the interpreter search path. Later setuptools, which needs to generate metadata as well, would use ``setup.py develop`` to install ``.egg-link`` files into ``site-packages``. Now that ``setup.py`` is no longer required we need a new mechanism for defining editable packages. This document describes a PEP-517 style method for editable packages.
  

Rationale
=========

PEP-517 [1]_ deferred "Editable installs", meaning non-``setup.py`` distributions lacked that feature. The only way to retain ``editable`` installs for these distributions was to provide a compatible ``setup.py develop`` implementation. By definining an editable hook other build frontends gain parity with ``setup.py``.

The Mechanism
=============

This PEP adds a single optional hook to the PEP-517 backend interface. The hook is used to build a wheel that, when installed,
allows that distribution to be imported from its source folder. This was traditionally done by adding the package's source folder to the interpreter search path. It can be done more precisely by producing a proxy module that replaces itself with the target module on import.

build_wheel_for_editable
------------------------

:: 

  def build_wheel_for_editable(
      wheel_directory,
      scheme=scheme, 
      metadata_directory=metadata_directory,
      config_settings=None):
      ...

``scheme``: a dictionary of installation categories ``{ 'purelib': '/home/py/.../site-packages', 'platlib': '...'}``. This makes it possible to use relative paths to the source code, which might help the interpreter find the package after
the root path changes with ``chroot`` or similar.

Must build a ``.whl`` file, and place it in the specified ``wheel_directory``. It
must return the basename (not the full path) of the .whl file it creates,
as a unicode string.

May do an in-place build of the distribution as a side effect so that any extension modules or other built artifacts are ready to be used.

The filename for the “editable” wheel need not use the same tags as ``build_wheel`` but must be tagged as compatible with the system.

If the build frontend has previously called ``prepare_metadata_for_build_wheel``
and depends on the wheel resulting from this call to have metadata
matching this earlier call, then it should provide the path to the created
.dist-info directory as the metadata_directory argument.

Backends which do not provide the ``prepare_metadata_for_build_wheel`` hook may
either silently ignore the metadata_directory parameter to build_wheel_for_editable, or else raise an exception when it is set to anything other than None.

An ‘editable’ wheel uses the wheel format not for distribution but as ephemeral communication between the build system and the front end. This avoids having the build backend install anything directly, but these wheels should not be cached or distributed.

What to put in the wheel
------------------------

https://github.com/pfmoore/editables/ shows how to build proxy modules that provide a high quality “editable” installation. It accepts a list of modules to include, and hide. When imported, these proxy modules replace themselves with the code from the source tree. Path-based methods make all scripts under a path importable, often including the project's own ``setup.py`` and other scripts that would not be part of a normal installation. The proxy strategy can achieve a higher level of fidelity than path-based methods.

References
==========

.. [1] PEP 517, A build-system independent format for source trees
   (http://www.python.org/dev/peps/pep-0517)


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
