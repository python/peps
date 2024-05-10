:orphan:

Appendix: Licensing Examples
============================

Abstract
--------

This document contains guidance on PEP 639 application in the
real-life :ref:`examples <639-examples>`.


.. _639-examples:

Examples
--------

.. _639-example-basic:

Basic example
'''''''''''''

The Setuptools project itself, as of `version 59.1.1 <setuptools5911_>`__,
does not use the ``License`` field in its own project source metadata.
Further, it no longer explicitly specifies ``license_file``/``license_files``
as it did previously, since Setuptools relies on its own automatic
inclusion of license-related files matching common patterns,
such as the ``LICENSE`` file it uses.

It includes the following license-related metadata in its ``setup.cfg``:

.. code-block:: ini

    [metadata]
    classifiers =
        License :: OSI Approved :: MIT License

The simplest migration to PEP 639 would consist of using this instead:

.. code-block:: ini

    [metadata]
    license_expression = MIT

Or, in the ``[project]`` table of ``pyproject.toml``:

.. code-block:: toml

    [project]
    license = "MIT"

The output Core Metadata for the distribution packages would then be:

.. code-block:: email

    License-Expression: MIT
    License-File: LICENSE

The ``LICENSE`` file would be stored at ``/setuptools-${VERSION}/LICENSE``
in the sdist and ``/setuptools-${VERSION}.dist-info/licenses/LICENSE``
in the wheel, and unpacked from there into the site directory (e.g.
``site-packages``) on installation; ``/`` is the root of the respective archive
and ``${VERSION}`` the version of the Setuptools release in the Core Metadata.


.. _639-example-advanced:

Advanced example
''''''''''''''''

Suppose Setuptools were to include the licenses of the third-party projects
that are vendored in the ``setuptools/_vendor/`` and ``pkg_resources/_vendor``
directories; specifically:

.. code-block:: text

    packaging==21.2
    pyparsing==2.2.1
    ordered-set==3.1.1
    more_itertools==8.8.0

The license expressions for these projects are:

.. code-block:: text

    packaging: Apache-2.0 OR BSD-2-Clause
    pyparsing: MIT
    ordered-set: MIT
    more_itertools: MIT

A comprehensive license expression covering both Setuptools
proper and its vendored dependencies would contain these metadata,
combining all the license expressions into one. Such an expression might be:

.. code-block:: text

    MIT AND (Apache-2.0 OR BSD-2-Clause)

In addition, per the requirements of the licenses, the relevant license files
must be included in the package. Suppose the ``LICENSE`` file contains the text
of the MIT license and the copyrights used by Setuptools, ``pyparsing``,
``more_itertools`` and ``ordered-set``; and the ``LICENSE*`` files in the
``setuptools/_vendor/packaging/`` directory contain the Apache 2.0 and
2-clause BSD license text, and the Packaging copyright statement and
`license choice notice <packaginglicense_>`__.

Specifically, we assume the license files are located at the following
paths in the project source tree (relative to the project root and
``pyproject.toml``):

.. code-block:: ini

    LICENSE
    setuptools/_vendor/packaging/LICENSE
    setuptools/_vendor/packaging/LICENSE.APACHE
    setuptools/_vendor/packaging/LICENSE.BSD

Putting it all together, our ``setup.cfg`` would be:

.. code-block:: ini

    [metadata]
    license_expression = MIT AND (Apache-2.0 OR BSD-2-Clause)
    license_files =
        LICENSE
        setuptools/_vendor/packaging/LICENSE
        setuptools/_vendor/packaging/LICENSE.APACHE
        setuptools/_vendor/packaging/LICENSE.BSD

In the ``[project]`` table of ``pyproject.toml``, with license files
specified explicitly via the ``paths`` subkey, this would look like:

.. code-block:: toml

    [project]
    license = "MIT AND (Apache-2.0 OR BSD-2-Clause)"
    license-files.paths = [
        "LICENSE",
        "setuptools/_vendor/LICENSE",
        "setuptools/_vendor/LICENSE.APACHE",
        "setuptools/_vendor/LICENSE.BSD",
    ]

Or alternatively, matched via glob patterns, this could be:

.. code-block:: toml

    [project]
    license = "MIT AND (Apache-2.0 OR BSD-2-Clause)"
    license-files.globs = [
        "LICENSE*",
        "setuptools/_vendor/LICENSE*",
    ]

With either approach, the output Core Metadata in the distribution
would be:

.. code-block:: email

    License-Expression: MIT AND (Apache-2.0 OR BSD-2-Clause)
    License-File: LICENSE
    License-File: setuptools/_vendor/packaging/LICENSE
    License-File: setuptools/_vendor/packaging/LICENSE.APACHE
    License-File: setuptools/_vendor/packaging/LICENSE.BSD

In the resulting sdist, with ``/`` as the root of the archive and ``${VERSION}``
the version of the Setuptools release specified in the Core Metadata,
the license files would be located at the paths:

.. code-block:: shell

    /setuptools-${VERSION}/LICENSE
    /setuptools-${VERSION}/setuptools/_vendor/packaging/LICENSE
    /setuptools-${VERSION}/setuptools/_vendor/packaging/LICENSE.APACHE
    /setuptools-${VERSION}/setuptools/_vendor/packaging/LICENSE.BSD

In the built wheel, with ``/`` being the root of the archive and
``{version}`` as the previous, the license files would be stored at:

.. code-block:: shell

    /setuptools-${VERSION}.dist-info/licenses/LICENSE
    /setuptools-${VERSION}.dist-info/licenses/setuptools/_vendor/packaging/LICENSE
    /setuptools-${VERSION}.dist-info/licenses/setuptools/_vendor/packaging/LICENSE.APACHE
    /setuptools-${VERSION}.dist-info/licenses/setuptools/_vendor/packaging/LICENSE.BSD

Finally, in the installed project, with ``site-packages`` being the site dir
and ``{version}`` as the previous, the license files would be installed to:

.. code-block:: shell

    site-packages/setuptools-${VERSION}.dist-info/licenses/LICENSE
    site-packages/setuptools-${VERSION}.dist-info/licenses/setuptools/_vendor/packaging/LICENSE
    site-packages/setuptools-${VERSION}.dist-info/licenses/setuptools/_vendor/packaging/LICENSE.APACHE
    site-packages/setuptools-${VERSION}.dist-info/licenses/setuptools/_vendor/packaging/LICENSE.BSD


.. _639-example-expression:

Expression examples
'''''''''''''''''''

Some additional examples of valid ``License-Expression`` values:

.. code-block:: email

    License-Expression: MIT
    License-Expression: BSD-3-Clause
    License-Expression: MIT AND (Apache-2.0 OR BSD-2-clause)
    License-Expression: MIT OR GPL-2.0-or-later OR (FSFUL AND BSD-2-Clause)
    License-Expression: GPL-3.0-only WITH Classpath-Exception-2.0 OR BSD-3-Clause
    License-Expression: LicenseRef-Public-Domain OR CC0-1.0 OR Unlicense
    License-Expression: LicenseRef-Proprietary


.. _packaginglicense: https://github.com/pypa/packaging/blob/21.2/LICENSE
.. _setuptools5911: https://github.com/pypa/setuptools/blob/v59.1.1/setup.cfg
