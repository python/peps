:orphan:

Appendix: License Documentation in Python and Other Projects
============================================================

Abstract
--------

There are multiple ways used or recommended to document licenses.
This document contains the results of a comprehensive survey of license
documentation in Python and other languages.

The key takeaways from the survey, which have guided the recommendations of
PEP 639, are as follows:

- Most package formats use a single ``License`` field.

- Many modern package systems use some form of :term:`license expression`
  to optionally combine more than one :term:`license identifier` together.
  SPDX and SPDX-like syntaxes are the most popular in use.

- SPDX license identifiers are becoming the de facto way to reference common
  licenses everywhere, whether or not a full license expression syntax is used.

- Several package formats support documenting both a license expression and the
  paths of the corresponding files that contain the license text. Most Free and
  Open Source Software licenses require package authors to include their full
  text in a :term:`Distribution Package`.


.. _639-license-doc-python:

License Documentation in Python
-------------------------------

.. _639-license-doc-core-metadata:

Core Metadata
'''''''''''''

There are two overlapping Core Metadata fields to document a license: the
license ``Classifier`` `strings <classifiers_>`__ prefixed with ``License ::``
and the ``License`` `field <licensefield_>`__ as free text.

The Core Metadata ``License`` field documentation is currently:

.. code-block:: rst

    License
    =======

    .. versionadded:: 1.0

    Text indicating the license covering the distribution where the license
    is not a selection from the "License" Trove classifiers. See
    :ref:`"Classifier" <metadata-classifier>` below.
    This field may also be used to specify a
    particular version of a license which is named via the ``Classifier``
    field, or to indicate a variation or exception to such a license.

    Examples::

        License: This software may only be obtained by sending the
                author a postcard, and then the user promises not
                to redistribute it.

        License: GPL version 3, excluding DRM provisions

Even though there are two fields, it is at times difficult to convey anything
but simpler licensing. For instance, some classifiers lack precision
(GPL without a version) and when multiple license classifiers are
listed, it is not clear if both licenses must apply, or the user may choose
between them. Furthermore, the list of available license classifiers
is rather limited and out-of-date.


.. _639-license-doc-setuptools-wheel:

Setuptools and Wheel
''''''''''''''''''''

Beyond a license code or qualifier, license text files are documented and
included in a built package either implicitly or explicitly,
and this is another possible source of confusion:

- In the `Setuptools <setuptoolssdist_>`__ and `Wheel <wheels_>`__ projects,
  license files are automatically added to the distribution (at their source
  location in a source distribution/sdist, and in the ``.dist-info``
  directory of a built wheel) if they match one of a number of common license
  file name patterns (``LICEN[CS]E*``, ``COPYING*``, ``NOTICE*`` and
  ``AUTHORS*``). Alternatively, a package author can specify a list of license
  file paths to include in the built wheel under the ``license_files`` key in
  the ``[metadata]`` section of the project's ``setup.cfg``, or as an argument
  to the ``setuptools.setup()`` function. At present, following the Wheel
  project's lead, Setuptools flattens the collected license files into the
  metadata directory, clobbering files with the same name, and dumps license
  files directly into the top-level ``.dist-info`` directory, but there is a
  `desire to resolve both these issues <setuptoolsfiles_>`__,
  contingent on PEP 639 being accepted.

- Both tools also support an older, singular ``license_file`` parameter that
  allows specifying only one license file to add to the distribution, which
  has been deprecated for some time but still sees `some use <pipsetup_>`__.

- Following the publication of an earlier draft of PEP 639, Setuptools
  `added support <setuptoolspep639_>`__ for ``License-File`` in distribution
  metadata as described in this specification. This allows other tools
  consuming the resulting metadata to unambiguously locate the license file(s)
  for a given package.


.. _639-license-doc-pypug:

PyPA Packaging Guide and Sample Project
'''''''''''''''''''''''''''''''''''''''

Both the `PyPA beginner packaging tutorial <packagingtuttxt_>`__ and its more
comprehensive `packaging guide <packagingguidetxt_>`__ state that it is
important that every package include a license file. They point to the
``LICENSE.txt`` in the official PyPA sample project as an example, which is
`explicitly listed <samplesetupcfg_>`__ under the ``license_files`` key in
its ``setup.cfg``, following existing practice formally specified by PEP 639.

Both the `beginner packaging tutorial <packagingtutkey_>`__ and the
`sample project <samplesetuppy_>`__ only use classifiers to declare a
package's license, and do not include or mention the ``License`` field.
The `full packaging guide <licensefield_>`__ does mention this field, but
states that authors should use the license classifiers instead, unless the
project uses a non-standard license (which the guide discourages).


.. _639-license-doc-source-files:

Python source code files
''''''''''''''''''''''''

**Note:** Documenting licenses in source code is not in the scope of PEP 639.

Beside using comments and/or ``SPDX-License-Identifier`` conventions, the
license is `sometimes <pycode_>`__ documented in Python code files using
a "dunder" module-level constant, typically named ``__license__``.

This convention, while perhaps somewhat antiquated, is recognized by the
built-in ``help()`` function and the standard ``pydoc`` module.
The dunder variable will show up in the ``help()`` DATA section for a module.


.. _639-license-doc-other-projects:

License Documentation in Other Projects
---------------------------------------

Linux distribution packages
'''''''''''''''''''''''''''

**Note:** in most cases, the texts of the most common licenses are included
globally in a shared documentation directory (e.g. ``/usr/share/doc``).

- Debian documents package licenses with
  `machine readable copyright files <dep5_>`__.
  It defines its own license expression syntax and list of identifiers for
  common licenses, both of which are closely related to those of SPDX.

- `Fedora packages <fedora_>`__ specify how to include
  `License Texts <fedoratext_>`__ and use a
  `License field <fedoralicense_>`__ that must be filled
  with appropriate short license identifier(s) from an extensive list
  of `"Good Licenses" <fedoralist_>`__. Fedora uses SPDX
  license expression syntax.

- `OpenSUSE packages <opensuse_>`__ use SPDX license expressions with
  SPDX license IDs and a
  `list of additional license identifiers <opensuselist_>`__.

- `Gentoo ebuild <gentoo_>`__ uses a ``LICENSE`` variable.
  This field is specified in `GLEP-0023 <glep23_>`__ and in the
  `Gentoo development manual <gentoodev_>`__.
  Gentoo also defines a list of allowed licenses and a license expression
  syntax, which is rather different from SPDX.

- The `FreeBSD package Makefile <freebsd_>`__ provides ``LICENSE`` and
  ``LICENSE_FILE`` fields with a list of custom license symbols. For
  non-standard licenses, FreeBSD recommends using ``LICENSE=UNKNOWN`` and
  adding ``LICENSE_NAME`` and ``LICENSE_TEXT`` fields, as well as sophisticated
  ``LICENSE_PERMS`` to qualify the license permissions and ``LICENSE_GROUPS``
  to document a license grouping. The ``LICENSE_COMB`` allows documenting more
  than one license and how they apply together, forming a custom license
  expression syntax. FreeBSD also recommends the use of
  ``SPDX-License-Identifier`` in source code files.

- `Arch Linux PKGBUILD <archinux_>`__ defines its
  `own license identifiers <archlinuxlist_>`__.
  The value ``'unknown'`` can be used if the license is not defined.

- `OpenWRT ipk packages <openwrt_>`__ use the ``PKG_LICENSE`` and
  ``PKG_LICENSE_FILES`` variables and recommend the use of SPDX License
  identifiers.

- `NixOS uses SPDX identifiers <nixos_>`__ and some extra license IDs
  in its license field.

- GNU Guix (based on NixOS) has a single License field, uses its own
  `license symbols list <guix_>`__ and specifies how to use one license or a
  `list of them <guixlicense_>`__.

- `Alpine Linux packages <alpine_>`__ recommend using SPDX identifiers in the
  license field.


Language and application packages
'''''''''''''''''''''''''''''''''

- In Java, `Maven POM <maven_>`__ defines a ``licenses`` XML tag with a list
  of licenses, each with a name, URL, comments and "distribution" type.
  This is not mandatory, and the content of each field is not specified.

- The `JavaScript NPM package.json <npm_>`__ uses a single license field with
  a SPDX license expression, or the ``UNLICENSED`` ID if none is specified.
  A license file can be referenced as an alternative using
  ``SEE LICENSE IN <filename>`` in the single ``license`` field.

- `Rubygems gemspec <gem_>`__ specifies either a single or list of license
  strings. The relationship between multiple licenses in a
  list is not specified. They recommend using SPDX license identifiers.

- `CPAN Perl modules <perl_>`__ use a single license field, which is either a
  single or a list of strings. The relationship between the licenses in
  a list is not specified. There is a list of custom license identifiers plus
  these generic identifiers: ``open_source``, ``restricted``, ``unrestricted``,
  ``unknown``.

- `Rust Cargo <cargo_>`__ specifies the use of an SPDX license expression
  (v2.1) in the ``license`` field. It also supports an alternative expression
  syntax using slash-separated SPDX license identifiers, and there is also a
  ``license_file`` field. The `crates.io package registry <cratesio_>`__
  requires that either ``license`` or ``license_file`` fields are set when
  uploading a package.

- `PHP composer.json <composer_>`__ uses a ``license`` field with
  an SPDX license ID or ``proprietary``. The ``license`` field is either a
  single string with resembling the SPDX license expression syntax with
  ``and`` and ``or`` keywords; or is a list of strings if there is a
  (disjunctive) choice of licenses.

- `NuGet packages <nuget_>`__ previously used only a simple license URL, but
  now specify using a SPDX license expression and/or the path to a license
  file within the package. The NuGet.org repository states that they only
  accept license expressions that are "approved by the Open Source Initiative
  or the Free Software Foundation."

- Go language modules ``go.mod`` have no provision for any metadata beyond
  dependencies. Licensing information is left for code authors and other
  community package managers to document.

- The `Dart/Flutter spec <flutter_>`__ recommends using a single ``LICENSE``
  file that should contain all the license texts, each separated by a line
  with 80 hyphens.

- The `JavaScript Bower <bower_>`__ ``license`` field is either a single string
  or list of strings using either SPDX license identifiers, or a path/URL
  to a license file.

- The `Cocoapods podspec <cocoapod_>`__ ``license`` field is either a single
  string, or a mapping with ``type``, ``file`` and ``text`` keys.
  This is mandatory unless there is a ``LICENSE``/``LICENCE`` file provided.

- `Haskell Cabal <cabal_>`__ accepts an SPDX license expression since
  version 2.2. The version of the SPDX license list used is a function of
  the Cabal version. The specification also provides a mapping between
  legacy (pre-SPDX) and SPDX license Identifiers. Cabal also specifies a
  ``license-file(s)`` field that lists license files to be installed with
  the package.

- `Erlang/Elixir mix/hex package <mix_>`__ specifies a ``licenses`` field as a
  required list of license strings, and recommends using SPDX license
  identifiers.

- `D Langanguage dub packages <dub_>`__ define their own list of license
  identifiers and license expression syntax, similar to the SPDX standard.

- The `R Package DESCRIPTION <cran_>`__ defines its own sophisticated license
  expression syntax and list of licenses identifiers. R has a unique way of
  supporting specifiers for license versions (such as ``LGPL (>= 2.0, < 3)``)
  in its license expression syntax.


Other ecosystems
''''''''''''''''

- The ``SPDX-License-Identifier`` `header <spdxid_>`__ is a simple
  convention to document the license inside a file.

- The `Free Software Foundation (FSF) <fsf_>`__ promotes the use of
  SPDX license identifiers for clarity in the `GPL <gnu_>`__ and other
  versioned free software licenses.

- The Free Software Foundation Europe (FSFE) `REUSE project <reuse_>`__
  promotes using ``SPDX-License-Identifier``.

- The `Linux kernel <linux_>`__ uses ``SPDX-License-Identifier``
  and parts of the FSFE REUSE conventions to document its licenses.

- `U-Boot <uboot_>`__ spearheaded using ``SPDX-License-Identifier`` in code
  and now follows the Linux approach.

- The Apache Software Foundation projects use `RDF DOAP <apache_>`__ with
  a single license field pointing to SPDX license identifiers.

- The `Eclipse Foundation <eclipse_>`__ promotes using
  ``SPDX-license-Identifiers``.

- The `ClearlyDefined project <clearlydefined_>`__ promotes using SPDX
  license identifiers and expressions to improve license clarity.

- The `Android Open Source Project <android_>`__ uses ``MODULE_LICENSE_XXX``
  empty tag files, where ``XXX`` is a license code such as ``BSD``, ``APACHE``,
  ``GPL``, etc. It also uses a ``NOTICE`` file that contains license and
  notice texts.


.. _alpine: https://wiki.alpinelinux.org/wiki/Creating_an_Alpine_package#license
.. _android: https://github.com/aosp-mirror/platform_external_tcpdump/blob/android-platform-12.0.0_r1/MODULE_LICENSE_BSD
.. _apache: https://svn.apache.org/repos/asf/allura/doap_Allura.rdf
.. _archinux: https://wiki.archlinux.org/title/PKGBUILD#license
.. _archlinuxlist: https://archlinux.org/packages/core/any/licenses/files/
.. _bower: https://github.com/bower/spec/blob/b00c4403e22e3f6177c410ed3391b9259687e461/json.md#license
.. _cabal: https://cabal.readthedocs.io/en/3.6/cabal-package.html?highlight=license#pkg-field-license
.. _cargo: https://doc.rust-lang.org/cargo/reference/manifest.html#package-metadata
.. _classifiers: https://pypi.org/classifiers
.. _clearlydefined: https://clearlydefined.io
.. _cocoapod: https://guides.cocoapods.org/syntax/podspec.html#license
.. _composer: https://getcomposer.org/doc/04-schema.md#license
.. _conda: https://docs.conda.io/projects/conda-build/en/stable/resources/define-metadata.html#about-section
.. _cran: https://cran.r-project.org/doc/manuals/r-release/R-exts.html#Licensing
.. _cratesio: https://doc.rust-lang.org/cargo/reference/registries.html#publish
.. _dep5: https://dep-team.pages.debian.net/deps/dep5/
.. _dub: https://dub.pm/package-format-json.html#licenses
.. _eclipse: https://www.eclipse.org/legal/epl-2.0/faq.php
.. _fedora: https://docs.fedoraproject.org/en-US/packaging-guidelines/LicensingGuidelines/
.. _fedoralicense: https://docs.fedoraproject.org/en-US/packaging-guidelines/LicensingGuidelines/#_valid_license_short_names
.. _fedoralist: https://fedoraproject.org/wiki/Licensing:Main?rd=Licensing#Good_Licenses
.. _fedoratext: https://docs.fedoraproject.org/en-US/packaging-guidelines/LicensingGuidelines/#_license_text
.. _flit: https://flit.readthedocs.io/en/stable/pyproject_toml.html
.. _flutter: https://flutter.dev/docs/development/packages-and-plugins/developing-packages#adding-licenses-to-the-license-file
.. _freebsd: https://docs.freebsd.org/en/books/porters-handbook/makefiles/#licenses
.. _fsf: https://www.fsf.org/blogs/rms/rms-article-for-claritys-sake-please-dont-say-licensed-under-gnu-gpl-2
.. _gem: https://guides.rubygems.org/specification-reference/#license=
.. _gentoo: https://devmanual.gentoo.org/ebuild-writing/variables/index.html#license
.. _gentoodev: https://devmanual.gentoo.org/general-concepts/licenses/index.html
.. _glep23: https://www.gentoo.org/glep/glep-0023.html
.. _gnu: https://www.gnu.org/licenses/identify-licenses-clearly.html
.. _guix: https://git.savannah.gnu.org/cgit/guix.git/tree/guix/licenses.scm?h=v1.3.0
.. _guixlicense: https://guix.gnu.org/manual/en/html_node/package-Reference.html#index-license_002c-of-packages
.. _licensefield: https://packaging.python.org/guides/distributing-packages-using-setuptools/#license
.. _linux: https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/Documentation/process/license-rules.rst
.. _maven: https://maven.apache.org/pom.html#Licenses
.. _mix: https://hex.pm/docs/publish
.. _npm: https://docs.npmjs.com/cli/v8/configuring-npm/package-json#license
.. _nixos: https://github.com/NixOS/nixpkgs/blob/21.05/lib/licenses.nix
.. _nuget: https://docs.microsoft.com/en-us/nuget/reference/nuspec#licenseurl
.. _opensuse: https://en.opensuse.org/openSUSE:Packaging_guidelines#Licensing
.. _opensuselist: https://docs.google.com/spreadsheets/d/14AdaJ6cmU0kvQ4ulq9pWpjdZL5tkR03exRSYJmPGdfs/pub
.. _openwrt: https://openwrt.org/docs/guide-developer/packages#buildpackage_variables
.. _packagingguidetxt: https://packaging.python.org/guides/distributing-packages-using-setuptools/#license-txt
.. _packagingtutkey: https://packaging.python.org/tutorials/packaging-projects/#configuring-metadata
.. _packagingtuttxt: https://packaging.python.org/tutorials/packaging-projects/#creating-a-license
.. _pbr: https://docs.openstack.org/pbr/latest/user/features.html
.. _perl: https://metacpan.org/pod/CPAN::Meta::Spec#license
.. _pipsetup: https://github.com/pypa/pip/blob/21.3.1/setup.cfg#L114
.. _poetry: https://python-poetry.org/docs/pyproject/#license
.. _pycode: https://github.com/search?l=Python&q=%22__license__%22&type=Code
.. _reuse: https://reuse.software/
.. _samplesetupcfg: https://github.com/pypa/sampleproject/blob/3a836905fbd687af334db16b16c37cf51dcbc99c/setup.cfg
.. _samplesetuppy: https://github.com/pypa/sampleproject/blob/3a836905fbd687af334db16b16c37cf51dcbc99c/setup.py#L98
.. _setuptoolssdist: https://github.com/pypa/setuptools/pull/1767
.. _setuptoolsfiles: https://github.com/pypa/setuptools/issues/2739
.. _setuptoolspep639: https://github.com/pypa/setuptools/pull/2645
.. _spdxid: https://spdx.dev/ids/
.. _uboot: https://www.denx.de/wiki/U-Boot/Licensing
.. _wheels: https://github.com/pypa/wheel/blob/0.37.0/docs/user_guide.rst#including-license-files-in-the-generated-wheel-file
