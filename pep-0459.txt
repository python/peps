PEP: 459
Title: Standard Metadata Extensions for Python Software Packages
Version: $Revision$
Last-Modified: $Date$
Author: Nick Coghlan <ncoghlan@gmail.com>
BDFL-Delegate: Nick Coghlan <ncoghlan@gmail.com>
Discussions-To: Distutils SIG <distutils-sig@python.org>
Status: Draft
Type: Standards Track
Content-Type: text/x-rst
Requires: 426
Created: 11 Nov 2013
Post-History: 21 Dec 2013


Abstract
========

This PEP describes several standard extensions to the Python metadata.

Like all metadata extensions, each standard extension format is
independently versioned. Changing any of the formats requires an update
to this PEP, but does not require an update to the core packaging metadata.

.. note::

   These extensions may eventually be separated out into their own PEPs,
   but we're already suffering from PEP overload in the packaging
   metadata space.

   This PEP was initially created by slicing out large sections of earlier
   drafts of PEP 426 and making them extensions, so some of the specifics
   may still be rough in the new context.


Standard Extension Namespace
============================

The ``python`` project on the Python Package Index refers to the CPython
reference interpreter. This namespace is used as the namespace for the
standard metadata extensions.

The currently defined standard extensions are:

* ``python.details``
* ``python.project``
* ``python.integrator``
* ``python.exports``
* ``python.commands``
* ``python.constraints``

All standard extensions are currently at version ``1.0``, and thus the
``extension_metadata`` field may be omitted without losing access to any
functionality.


The ``python.details`` extension
================================

The ``python.details`` extension allows for more information to be provided
regarding the software distribution.

The ``python.details`` extension contains four custom subfields:

* ``license``: the copyright license for the distribution
* ``keywords``: package index keywords for the distribution
* ``classifiers``: package index Trove classifiers for the distribution
* ``document_names``: the names of additional metadata files

All of these fields are optional. Automated tools MUST operate correctly if
a distribution does not provide them, including failing cleanly when an
operation depending on one of these fields is requested.


License
-------

A short string summarising the license used for this distribution.

Note that distributions that provide this field should still specify any
applicable license Trove classifiers in the `Classifiers`_ field. Even
when an appropriate Trove classifier is available, the license summary can
be a good way to specify a particular version of that license, or to
indicate any variations or exception to the license.

This field SHOULD contain fewer than 512 characters and MUST contain fewer
than 2048.

This field SHOULD NOT contain any line breaks.

The full license text SHOULD be included as a separate file in the source
archive for the distribution. See `Document names`_ for details.

Example::

    "license": "GPL version 3, excluding DRM provisions"


Keywords
--------

A list of additional keywords to be used to assist searching for the
distribution in a larger catalog.

Example::

    "keywords": ["comfy", "chair", "cushions", "too silly", "monty python"]


Classifiers
-----------

A list of strings, with each giving a single classification value
for the distribution.  Classifiers are described in PEP 301 [2].

Example::

    "classifiers": [
      "Development Status :: 4 - Beta",
      "Environment :: Console (Text Based)",
      "License :: OSI Approved :: GNU General Public License v3 (GPLv3)"
    ]


Document names
--------------

Filenames for supporting documents included in the distribution's
``dist-info`` metadata directory.

The following supporting documents can be named:

* ``description``: a file containing a long description of the distribution
* ``license``: a file with the full text of the distribution's license
* ``changelog``: a file describing changes made to the distribution

Supporting documents MUST be included directly in the ``dist-info``
directory. Directory separators are NOT permitted in document names.

The markup format (if any) for the file is indicated by the file extension.
This allows index servers and other automated tools to render included
text documents correctly and provide feedback on rendering errors, rather
than having to guess the intended format.

If the filename has no extension, or the extension is not recognised, the
default rendering format MUST be plain text.

The following markup renderers SHOULD be used for the specified file
extensions:

* Plain text: ``.txt``, no extension, unknown extension
* reStructured Text: ``.rst``
* Markdown: ``.md``
* AsciiDoc: ``.adoc``, ``.asc``, ``.asciidoc``
* HTML: ``.html``, ``.htm``

Automated tools MAY render one or more of the specified formats as plain
text and MAY render other markup formats beyond those listed.

Automated tools SHOULD NOT make any assumptions regarding the maximum length
of supporting document content, except as necessary to protect the
integrity of a service.

Example::

    "document_names": {
        "description": "README.rst",
        "license": "LICENSE.rst",
        "changelog": "NEWS"
    }


The ``python.project`` extension
================================

The ``python.project`` extension allows for more information to be provided
regarding the creation and maintenance of the distribution.

The ``python.project`` extension contains three custom subfields:

* ``contacts``: key contact points for the distribution
* ``contributors``: other contributors to the distribution
* ``project_urls``: relevant URLs for the distribution


Contact information
-------------------

Details on individuals and organisations are recorded as mappings with
the following subfields:

* ``name``: the name of an individual or group
* ``email``: an email address (this may be a mailing list)
* ``url``: a URL (such as a profile page on a source code hosting service)
* ``role``: one of ``"author"``, ``"maintainer"`` or ``"contributor"``

The ``name`` subfield is required, the other subfields are optional.

If no specific role is stated, the default is ``contributor``.

Email addresses must be in the form ``local-part@domain`` where the
local-part may be up to 64 characters long and the entire email address
contains no more than 254 characters. The formal specification of the
format is in RFC 5322 (sections 3.2.3 and 3.4.1) and RFC 5321, with a more
readable form given in the informational RFC 3696 and the associated errata.

The defined contributor roles are as follows:

* ``author``: the original creator of a distribution
* ``maintainer``: the current lead contributor for a distribution, when
  they are not the original creator
* ``contributor``: any other individuals or organizations involved in the
  creation of the distribution

Contact and contributor metadata is optional. Automated tools MUST operate
correctly if a distribution does not provide it, including failing cleanly
when an operation depending on one of these fields is requested.


Contacts
--------

A list of contributor entries giving the recommended contact points for
getting more information about the project.

The example below would be suitable for a project that was in the process
of handing over from the original author to a new lead maintainer, while
operating as part of a larger development group.

Example::

    "contacts": [
      {
        "name": "Python Packaging Authority/Distutils-SIG",
        "email": "distutils-sig@python.org",
        "url": "https://bitbucket.org/pypa/"
      },
      {
        "name": "Samantha C.",
        "role": "maintainer",
        "email": "dontblameme@example.org"
      },
      {
        "name": "Charlotte C.",
        "role": "author",
        "email": "iambecomingasketchcomedian@example.com"
      }
    ]


Contributors
------------

A list of contributor entries for other contributors not already listed as
current project points of contact. The subfields within the list elements
are the same as those for the main contact field.

Example::

    "contributors": [
      {"name": "John C."},
      {"name": "Erik I."},
      {"name": "Terry G."},
      {"name": "Mike P."},
      {"name": "Graeme C."},
      {"name": "Terry J."}
    ]


Project URLs
------------

A mapping of arbitrary text labels to additional URLs relevant to the
project.

While projects are free to choose their own labels and specific URLs,
it is RECOMMENDED that home page, source control, issue tracker and
documentation links be provided using the labels in the example below.

URL labels MUST be treated as case insensitive by automated tools, but they
are not required to be valid Python identifiers. Any legal JSON string is
permitted as a URL label.

Example::

    "project_urls": {
      "Documentation": "https://distlib.readthedocs.org",
      "Home": "https://bitbucket.org/pypa/distlib",
      "Repository": "https://bitbucket.org/pypa/distlib/src",
      "Tracker": "https://bitbucket.org/pypa/distlib/issues"
    }


The ``python.integrator`` extension
===================================

Structurally, this extension is largely identical to the ``python.project``
extension (the extension name is the only difference).

However, where the ``project`` metadata refers to the upstream creators
of the software, the ``integrator`` metadata refers to the downstream
redistributor of a modified version.

If the software is being redistributed unmodified, then typically this
extension will not be used. However, if the software has been patched (for
example, backporting compatible fixes from a later version, or addressing
a platform compatibility issue), then this extension SHOULD be used, and
a local version label added to the distribution's version identifier.

If there are multiple redistributors in the chain, each one just overwrites
this extension with their particular metadata.


The ``python.exports`` extension
================================

Most Python distributions expose packages and modules for import through
the Python module namespace. Distributions may also expose other
interfaces when installed.

The ``python.exports`` extension contains three custom subfields:

* ``modules``: modules exported by the distribution
* ``namespaces``: namespace packages that the distribution contributes to
* ``exports``: other Python interfaces exported by the distribution


Export specifiers
-----------------

An export specifier is a string consisting of a fully qualified name, as
well as an optional extra name enclosed in square brackets. This gives the
following four possible forms for an export specifier::

   module
   module:name
   module[requires_extra]
   module:name[requires_extra]

.. note::

   The jsonschema file currently restricts qualified names using the
   Python 2 ASCII identifier rules. This may need to be reconsidered
   given the more relaxed identifier rules in Python 3.

The meaning of the subfields is as follows:

* ``module``: the module providing the export
* ``name``: if applicable, the qualified name of the export within the module
* ``requires_extra``: indicates the export will only work correctly if the
  additional dependencies named in the given extra are available in the
  installed environment

.. note::

   I tried this as a mapping with subfields, and it made the examples below
   unreadable. While this PEP is mostly for tool use, readability still
   matters to some degree for debugging purposes, and because I expect
   snippets of the format to be reused elsewhere.


Modules
-------

A list of qualified names of modules and packages that the distribution
provides for import.

.. note::

   The jsonschema file currently restricts qualified names using the
   Python 2 ASCII identifier rules. This may need to be reconsidered
   given the more relaxed identifier rules in Python 3.

For names that contain dots, the portion of the name before the final dot
MUST appear either in the installed module list or in the namespace package
list.

To help avoid name conflicts, it is RECOMMENDED that distributions provide
a single top level module or package that matches the distribution name
(or a lower case equivalent). This requires that the distribution name also
meet the requirements of a Python identifier, which are stricter than
those for distribution names). This practice will also make it easier to
find authoritative sources for modules.

Index servers SHOULD allow multiple distributions to publish the same
modules, but MAY notify distribution authors of potential conflicts.

Installation tools SHOULD report an error when asked to install a
distribution that provides a module that is also provided by a different,
previously installed, distribution.

Note that attempting to import some declared modules may result in an
exception if the appropriate extras are not installed.

Example::

    "modules": ["chair", "chair.cushions", "python_sketches.nobody_expects"]

.. note::

   Making this a list of export specifiers instead would allow a distribution
   to declare when a particular module requires a particular extra in order
   to run correctly. On the other hand, there's an argument to be made that
   that is the point where it starts to become worthwhile to split out a
   separate distribution rather than using extras.


Namespaces
----------

A list of qualified names of namespace packages that the distribution
contributes modules to.

.. note::

   The jsonschema file currently restricts qualified names using the
   Python 2 ASCII identifier rules. This may need to be reconsidered
   given the more relaxed identifier rules in Python 3.

On versions of Python prior to Python 3.3 (which provides native namespace
package support), installation tools SHOULD emit a suitable ``__init__.py``
file to properly initialise the namespace rather than using a distribution
provided file.

Installation tools SHOULD emit a warning and MAY emit an error if a
distribution declares a namespace package that conflicts with the name of
an already installed module or vice-versa.

Example::

    "namespaces": ["python_sketches"]


Exports
-------

The ``exports`` field is a mapping containing prefixed names as keys. Each
key identifies an export group containing one or more exports published by
the distribution.

Export group names are defined by distributions that will then make use of
the published export information in some way. The primary use case is for
distributions that support a plugin model: defining an export group allows
other distributions to indicate which plugins they provide, how they
can be imported and accessed, and which additional dependencies (if any)
are needed for the plugin to work correctly.

To reduce the chance of name conflicts, export group names SHOULD use a
prefix that corresponds to a module name in the distribution that defines
the meaning of the export group. This practice will also make it easier to
find authoritative documentation for export groups.

Each individual export group is then a mapping of arbitrary non-empty string
keys to export specifiers. The meaning of export names within an export
group is up to the distribution that defines the export group. Creating an
appropriate definition for the export name format can allow the importing
distribution to determine whether or not an export is relevant without
needing to import every exporting module.

Example::

    "exports": {
      "nose.plugins.0.10": {
        "chairtest": "chair:NosePlugin"
      }
    }


The ``python.commands`` extension
=================================

The ``python.commands`` extension contains three custom subfields:

* ``wrap_console``: console wrapper scripts to be generated by the installer
* ``wrap_gui``: GUI wrapper scripts to be generated by the installer
* ``prebuilt``: scripts created by the distribution's build process and
  installed directly to the configured scripts directory

``wrap_console`` and ``wrap_gui`` are both mappings of script names to
export specifiers. The script names must follow the same naming rules as
distribution names.

The export specifiers for wrapper scripts must refer to either a package
with a __main__ submodule (if no ``name`` subfield is given in the export
specifier) or else to a callable inside the named module.

Installation tools should generate appropriate wrappers as part of the
installation process.

.. note::

   Still needs more detail on what "appropriate wrappers" means. For now,
   refer to what setuptools and zc.buildout generate as wrapper scripts.

``prebuilt`` is a list of script paths, relative to the scripts directory in
a wheel file or following installation. They are provided for informational
purpose only - installing them is handled through the normal processes for
files created when building a distribution.

Build tools SHOULD mark this extension as requiring handling by installers.

Index servers SHOULD allow multiple distributions to publish the same
commands, but MAY notify distribution authors of potential conflicts.

Installation tools SHOULD report an error when asked to install a
distribution that provides a command that is also provided by a different,
previously installed, distribution.

Example::

    "python.commands": {
      "installer_must_handle": true,
      "wrap_console": [{"chair": "chair:run_cli"}],
      "wrap_gui": [{"chair-gui": "chair:run_gui"}],
      "prebuilt": ["reduniforms"]
    }


The ``python.constraints`` extension
====================================

The ``python.constraints`` extension contains two custom subfields:

* ``environments``: supported installation environments
* ``extension_metadata``: required exact matches in extension metadata
  fields published by other installed components

Build tools SHOULD mark this extension as requiring handling by installers.

Index servers SHOULD allow distributions to be uploaded with constraints
that cannot be satisfied using that index, but MAY notify distribution
authors of any such potential compatibility issues.

Installation tools SHOULD report an error if constraints are specified by
the distribution and the target installation environment fails to satisfy
them, MUST at least emit a warning, and MAY allow the user to
force the installation to proceed regardless.

Example::

    "python.constraints": {
      "installer_must_handle": true,
      "environments": ["python_version >= 2.6"],
      "extension_metadata": {
        "fortranlib": {
          "fortranlib.compatibility": {
            "fortran_abi": "openblas-g77"
          }
        }
      }
    }


Supported Environments
----------------------

The ``environments`` subfield is a list of strings specifying the
environments that the distribution explicitly supports. An environment is
considered supported if it matches at least one of the environment markers
given.

If this field is not given in the metadata, it is assumed that the
distribution supports any platform supported by Python.

Individual entries are environment markers, as described in :pep:`426`.

The two main uses of this field are to declare which versions of Python
and which underlying operating systems are supported.

Examples indicating supported Python versions::

   # Supports Python 2.6+
   "environments": ["python_version >= '2.6'"]

   # Supports Python 2.6+ (for 2.x) or 3.3+ (for 3.x)
   "environments": ["python_version >= '3.3'",
                    "'3.0' > python_version >= '2.6'"]

Examples indicating supported operating systems::

   # Windows only
   "environments": ["sys_platform == 'win32'"]

   # Anything except Windows
   "environments": ["sys_platform != 'win32'"]

   # Linux or BSD only
   "environments": ["'linux' in sys_platform",
                    "'bsd' in sys_platform"]

Example where the supported Python version varies by platform::

   # The standard library's os module has long supported atomic renaming
   # on POSIX systems, but only gained atomic renaming on Windows in Python
   # 3.3. A distribution that needs atomic renaming support for reliable
   # operation might declare the following supported environments.
   "environment": ["python_version >= '2.6' and sys_platform != 'win32'",
                   "python_version >= '3.3' and sys_platform == 'win32'"]


Extension metadata constraints
------------------------------

The ``extension_metadata`` subfield is a mapping from distribution names
to extension metadata snippets that are expected to exactly match the
metadata of the named distribution in the target installation environment.

Each submapping then consists of a mapping from metadata extension names to
the exact expected values of a subset of fields.

For example, a distribution called ``fortranlib`` may publish a different
FORTRAN ABI depending on how it is built, and any related projects that are
installed into the same runtime environment should use matching build
options. This can be handled by having the base distribution publish a
custom extension that indicates the build option that was used to create
the binary extensions::

    "extensions": {
      "fortranlib.compatibility": {
        "fortran_abi": "openblas-g77"
      }
    }

Other distributions that contain binary extensions that need to be compatible
with the base distribution would then define a suitable constraint in their
own metadata::

    "python.constraints": {
      "installer_must_handle": true,
      "extension_metadata": {
        "fortranlib": {
          "fortranlib.compatibility": {
            "fortran_abi": "openblas-g77"
          }
        }
      }
    }

This constraint specifies that:

* ``fortranlib`` must be installed (this should also be expressed as a
  normal dependency so that installers ensure it is satisfied)
* The installed version of ``fortranlib`` must include the custom
  ``fortranlib.compatibility`` extension in its published metadata
* The ``fortan_abi`` subfield of that extension must have the *exact*
  value ``openblas-g77``.

If all of these conditions are met (the distribution is installed, the
specified extension is included in the metadata, the specified subfields
have the exact specified value), then the constraint is considered to be
satisfied.

.. note::

  The primary intended use case here is allowing C extensions with additional
  ABI compatibility requirements to declare those in a way that any
  installation tool can enforce without needing to understand the details.
  In particular, many NumPy based scientific libraries need to be built
  using a consistent set of FORTRAN libraries, hence the "fortranlib"
  example.

  This is the reason there's no support for pattern matching or boolean
  logic: even the "simple" version of this extension is relatively
  complex, and there's currently no compelling rationale for making it
  more complicated than it already is.


Copyright
=========

This document has been placed in the public domain.


..
   Local Variables:
   mode: indented-text
   indent-tabs-mode: nil
   sentence-end-double-space: t
   fill-column: 70
   End:
