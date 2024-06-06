:orphan:

Appendix: User Scenarios
========================

Abstract
--------

This document contains guidance on PEP 639 application in the
real-life :ref:`user scenarios <639-user-scenarios>`.


.. _639-user-scenarios:

User Scenarios
--------------

The following covers the range of common use cases from a user perspective,
providing guidance for each. Do note that the following
should **not** be considered legal advice, and readers should consult a
licensed legal practitioner in their jurisdiction if they are unsure about
the specifics for their situation.


I have a private package that won't be distributed
''''''''''''''''''''''''''''''''''''''''''''''''''

If your package isn't shared publicly, i.e. outside your company,
organization or household, it *usually* isn't strictly necessary to include
a formal license, so you wouldn't necessarily have to do anything extra here.

However, it is still a good idea to include ``LicenseRef-Proprietary``
as a license expression in your package configuration, and/or a
copyright statement and any legal notices in a ``LICENSE.txt`` file
in the root of your project directory, which will be automatically
included by packaging tools.


I just want to share my own work without legal restrictions
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

While you aren't required to include a license, if you don't, no one has
`any permission to download, use or improve your work <dontchoosealicense_>`__,
so that's probably the *opposite* of what you actually want.
The `MIT license <mitlicense_>`__ is a great choice instead, as it's simple,
widely used and allows anyone to do whatever they want with your work
(other than sue you, which you probably also don't want).

To apply it, just paste `the text <chooseamitlicense_>`__ into a file named
``LICENSE.txt`` at the root of your repo, and add the year and your name to
the copyright line. Then, just add ``license = "MIT"`` under
``[project]`` in your ``pyproject.toml`` if your packaging tool supports it,
or in its config file/section. You're done!


I want to distribute my project under a specific license
''''''''''''''''''''''''''''''''''''''''''''''''''''''''

To use a particular license, simply paste its text into a ``LICENSE.txt``
file at the root of your repo, if you don't have it in a file starting with
``LICENSE`` or ``COPYING`` already, and add
``license = "LICENSE-ID"`` under ``[project]`` in your
``pyproject.toml`` if your packaging tool supports it, or else in its
config file. You can find the ``LICENSE-ID``
and copyable license text on sites like
`ChooseALicense <choosealicenselist_>`__ or `SPDX <spdxlist_>`__.

Many popular code hosts, project templates and packaging tools can add the
license file for you, and may support the expression as well in the future.


I maintain an existing package that's already licensed
''''''''''''''''''''''''''''''''''''''''''''''''''''''

If you already have license files and metadata in your project, you
should only need to make a couple of tweaks to take advantage of the new
functionality.

In your project config file, enter your license expression under
``license`` (``[project]`` table in ``pyproject.toml``),
or the equivalent for your packaging tool,
and make sure to remove any legacy ``license`` table subkeys or
``License ::`` classifiers. Your existing ``license`` value may already
be valid as one (e.g. ``MIT``, ``Apache-2.0 OR BSD-2-Clause``, etc);
otherwise, check the `SPDX license list <spdxlist_>`__ for the identifier
that matches the license used in your project.

Make sure to list your license files under ``license-files.paths``
or ``license-files.globs`` under ``[project]`` in ``pyproject.toml``
or else in your tool's configuration file.

See the :ref:`639-example-basic` for a simple but complete real-world demo
of how this works in practiced.
Packaging tools may support automatically converting legacy licensing
metadata; check your tool's documentation for more information.


My package includes other code under different licenses
'''''''''''''''''''''''''''''''''''''''''''''''''''''''

If your project includes code from others covered by different licenses,
such as vendored dependencies or files copied from other open source
software, you can construct a license expression
to describe the licenses involved and the relationship
between them.

In short, ``License-1 AND License-2`` mean that *both* licenses apply
to your project, or parts of it (for example, you included a file
under another license), and ``License-1 OR License-2`` means that
*either* of the licenses can be used, at the user's option (for example,
you want to allow users a choice of multiple licenses). You can use
parenthesis (``()``) for grouping to form expressions that cover even the most
complex situations.

In your project config file, enter your license expression under
``license`` (``[project]`` table of ``pyproject.toml``),
or the equivalent for your packaging tool,
and make sure to remove any legacy ``license`` table subkeys
or ``License ::`` classifiers.

Also, make sure you add the full license text of all the licenses as files
somewhere in your project repository. List the
relative path or glob patterns to each of them under ``license-files.paths``
or ``license-files.globs`` under ``[project]`` in ``pyproject.toml``
(if your tool supports it), or else in your tool's configuration file.

As an example, if your project was licensed MIT but incorporated
a vendored dependency (say, ``packaging``) that was licensed under
either Apache 2.0 or the 2-clause BSD, your license expression would
be ``MIT AND (Apache-2.0 OR BSD-2-Clause)``. You might have a
``LICENSE.txt`` in your repo root, and a ``LICENSE-APACHE.txt`` and
``LICENSE-BSD.txt`` in the ``_vendor`` subdirectory, so to include
all of them, you'd specify ``["LICENSE.txt", "_vendor/packaging/LICENSE*"]``
as glob patterns, or
``["LICENSE.txt", "_vendor/LICENSE-APACHE.txt", "_vendor/LICENSE-BSD.txt"]``
as literal file paths.

See a fully worked out :ref:`639-example-advanced` for an end-to-end
application of this to a real-world complex project, with many technical
details, and consult a `tutorial <spdxtutorial_>`__ for more help and examples
using SPDX identifiers and expressions.


.. _chooseamitlicense: https://choosealicense.com/licenses/mit/
.. _choosealicenselist: https://choosealicense.com/licenses/
.. _dontchoosealicense: https://choosealicense.com/no-permission/
.. _mitlicense: https://opensource.org/licenses/MIT
.. _spdxlist: https://spdx.org/licenses/
.. _spdxtutorial: https://github.com/david-a-wheeler/spdx-tutorial
