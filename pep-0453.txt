PEP: 453
Title: Explicit bootstrapping of pip in Python installations
Version: $Revision$
Last-Modified: $Date$
Author: Donald Stufft <donald@stufft.io>,
        Nick Coghlan <ncoghlan@gmail.com>
Status: Draft
Type: Process
Content-Type: text/x-rst
Created: 10-Aug-2013
Post-History: 30-Aug-2013


Abstract
========

This PEP proposes the inclusion of a method for explicitly bootstrapping
`pip`_ as the default package manager for Python. It also proposes that the
distributions of Python available via Python.org will automatically run this
explicit bootstrapping method and a recommendation to third party
redistributors of Python to also provide pip by default (in a way reasonable
for their distributions).

This PEP does *not* proposes the inclusion of pip itslef in the standard
library.


Proposal
========

This PEP proposes the inclusion of a ``getpip`` bootstrapping module in
Python 3.4, as well as in the upcoming maintenance releases of Python 2.7
and Python 3.3.


Rationale
=========

Installing a third party package into a freshly installed Python requires first
installing the package manager. This requires users ahead of time to know what
the package manager is, where to get them from, and how to install them. The
effect of this is that these external projects are required to either blindly
assume the user already has the package manager installed, needs to duplicate
the instructions and tell their users how to install the package manager, or
completely forgo the use of dependencies to ease installation concerns for
their users.

All of the available options have their own drawbacks.

If a project simply assumes a user already has the tooling then they get a
confusing error message when the installation command doesn't work. Some
operating may ease this pain by providing a global hook that looks for commands
that don't exist and suggest an OS package they can install to make the command
work.

If a project chooses to duplicate the installation instructions and tell their
users how to install the package manager before telling them how to install
their own project then whenever these instructions need updates they need
updating by every project that has duplicated them. This will inevitably not
happen in every case leaving many different instructions on how to install it
many of them broken or less than optimal. These additional instructions might
also confuse users who try to install the package manager a second time
thinking that it's part of the instructions of installing the project.

The problem of stale instructions can be alleviated by referencing `pip's
own bootstrapping instructions
<http://www.pip-installer.org/en/latest/installing.html>`__, but the user
experience involved still isn't good (especially on Windows, where
downloading and running a Python script with the default OS configuration is
significantly more painful than downloading and running a binary executable
or installer).

The projects that have decided to forgo dependencies all together are forced
to either duplicate the efforts of other projects by inventing their own
solutions to problems or are required to simply include the other projects
in their own source trees. Both of these options present their own problems
either in duplicating maintenance work across the ecosystem or potentially
leaving users vulnerable to security issues because the included code or
duplicated efforts are not automatically updated when upstream releases a new
version.

By providing the package manager by default it will be easier for users trying
to install these third party packages as well as easier for the people
distributing them as they no longer need to pick the lesser evil. This will
become more important in the future as the Wheel_ package format does not have
a built in "installer" in the form of ``setup.py`` so users wishing to install
a Wheel package will need an installer even in the simple case.

Reducing the burden of actually installing a third party package should also
decrease the pressure to add every useful module to the standard library. This
will allow additions to the standard library to focus more on why Python should
have a particular tool out of the box instead of needing to use the difficulty
in installing a package as justification for inclusion.


Explicit Bootstrapping
======================

An additional module called ``getpip`` will be added to the standard library
whose purpose is to install pip and any of its dependencies into the
appropriate location (most commonly site-packages). It will expose a single
callable named ``bootstrap()`` as well as offer direct execution via
``python -m getpip``. Options for installing it such as index server,
installation location (``--user``, ``--root``, etc) will also be available
to enable different installation schemes.

It is believed that users will want the most recent versions available to be
installed so that they can take advantage of the new advances in packaging.
Since any particular version of Python has a much longer staying power than
a version of pip in order to satisfy a user's desire to have the most recent
version the bootstrap will contact PyPI, find the latest version, download it,
and then install it. This process is security sensitive, difficult to get
right, and evolves along with the rest of packaging.

Instead of attempting to maintain a "mini pip" for the sole purpose of
installing pip the ``getpip`` module will, as an implementation detail, include
a private copy of pip which will be used to discover and install pip from PyPI.
It is important to stress that this private copy of pip is *only* an
implementation detail and it should *not* be relied on or assumed to exist.

Not all users will have network access to PyPI whenever they run the bootstrap.
In order to ensure that these users will still be able to bootstrap pip the
bootstrap will fallback to simply installing the included copy of pip.

This presents a balance between giving users the latest version of pip, saving
them from needing to immediately upgrade pip after bootstrapping it, and
allowing the bootstrap to work offline in situations where users might already
have packages downloaded that they wish to install.


Updating the Bundled pip
------------------------

In order to keep up with evolutions in packaging as well as providing users
who are using the offline installation method with as recent version as
possible the ``getpip`` module should be updates to the latest versions of
everything it bootstraps. During the preparation for any release of Python, a
script, provided as part of this PEP, should be run to update the bundled
packages to the latest versions.

This means that maintenance releases of the CPython installers will include
an updated version of the ``getpip`` bootstrap module.


Pre-installation
================

During the installation of Python from Python.org ``python -m getpip`` should
be executed. Leaving people using the Windows or OSX installers with a working
copy of pip once the installation has completed. The exact method of this is
left up to the maintainers of the installers however if the bootstrapping is
optional it should be opt out rather than opt in.

The Windows and OSX installers distributed by Python.org will automatically
attempt to run ``python -m getpip`` by default however the ``make install``
and ``make altinstall`` commands of the source distribution will not.

Keeping the pip bootstrapping as a separate step for make based
installations should minimise the changes CPython redistributors need to
make to their build processes. Avoiding the layer of indirection through
make for the getpip invocation also ensures those installing from a custom
source build can easily force an offline installation of pip, install it
from a private index server, or skip installing pip entirely.


Python Virtual Environments
===========================

Python 3.3 included a standard library approach to virtual Python environments
through the ``venv`` module. Since it's release it has become clear that very
few users have been willing to use this feature in part due to the lack of
an installer present by default inside of the virtual environment. They have
instead opted to continue using the ``virtualenv`` package which *does* include
pip installed by default.

To make the ``venv`` more useful to users it will be modified to issue the
pip bootstrap by default inside of the new environment while creating it. This
will allow people the same convenience inside of the virtual environment as
this PEP provides outside of it as well as bringing the ``venv`` module closer
to feature parity with the external ``virtualenv`` package making it a more
suitable replacement.


Recommendations for Downstream Distributors
===========================================

A common source of Python installations are through downstream distributors
such as the various Linux Distributions [#ubuntu]_ [#debian]_ [#fedora]_, OSX
package managers [#homebrew]_, or python specific tools [#conda]_. In order to
provide a consistent, user friendly experience to all users of Python
regardless of how they attained Python this PEP recommends and asks that
downstream distributors:

* Ensure that whenever Python is installed pip is also installed.

  * This may take the form of separate with dependencies on each either so that
    installing the python package installs the pip package and installing the
    pip package installs the Python package.

* Do not remove the bundled copy of pip.

  * This is required for offline installation of pip into a virtual environment.
  * This is similar to the existing ``virtualenv`` package for which many
    downstream distributors have already made exception to the common
    "debundling" policy.
  * This does mean that if ``pip`` needs to be updated due to a security
    issue, so does the bundled version in the ``getpip`` bootstrap module

* Migrate build systems to utilize `pip`_ and `Wheel`_ instead of directly
  using ``setup.py``.

  * This will ensure that downstream packages can utilize the new formats which
    will not have a ``setup.py`` easier.

* Ensure that all features of this PEP continue to work with any modifications
  made.

  * Online installation of the latest version of pip into a global or virtual
    python environment using ``python -m getpip``.
  * Offline installation of the bundled version of pip into a global or virtual
    python environment using ``python -m getpip``.
  * ``pip install --upgrade pip`` in a global installation should not affect
    any already created virtual environments.
  * ``pip install --upgrade pip`` in a virtual environment should not affect
    the global installation.


Policies & Governance
=====================

The maintainers of the bundled software and the CPython core team will work
together in order to address the needs of both. The bundled software will still
remain external to CPython and this PEP does not include CPython subsuming the
responsibilities or decisions of the bundled software. This PEP aims to
decrease the burden on end users wanting to use third party packages and the
decisions inside it are pragmatic ones that represent the trust that the
Python community has placed in the authors and maintainers of the bundled
software.


Backwards Compatibility
-----------------------

The public API of the ``getpip`` module itself will fall under the typical
backwards compatibility policy of Python for its standard library. The
externally developed software that this PEP bundles does not.


Security Releases
-----------------

Any security update that affects the ``getpip`` module will be shared prior to
release with the PSRT. The PSRT will then decide if the issue inside warrants
a security release of Python.


Appendix: Rejected Proposals
============================


Implicit Bootstrap
------------------

`PEP439`_, the predecessor for this PEP, proposes it's own solution. Its
solution involves shipping a fake ``pip`` command that when executed would
implicitly bootstrap and install pip if it does not already exist. This has
been rejected because it is too "magical". It hides from the end user when
exactly the pip command will be installed or that it is being installed at all.
It also does not provide any recommendations or considerations towards
downstream packagers who wish to manage the globally installed pip through the
mechanisms typical for their system.


Including pip In the Standard Library
-------------------------------------

Similar to this PEP is the proposal of just including pip in the standard
library. This would ensure that Python always includes pip and fixes all of the
end user facing problems with not having pip present by default. This has been
rejected because we've learned through the inclusion and history of
``distutils`` in the standard library that losing the ability to update the
packaging tools independently can leave the tooling in a state of constant
limbo. Making it unable to ever reasonably evolve in a timeframe that actually
affects users as any new features will not be available to the general
population for *years*.

Allowing the packaging tools to progress separately from the Python release
and adoption schedules allows the improvements to be used by *all* members
of the Python community and not just those able to live on the bleeding edge
of Python releases.


.. _Wheel: http://www.python.org/dev/peps/pep-0427/
.. _pip: http://www.pip-installer.org
.. _setuptools: https://pypi.python.org/pypi/setuptools
.. _PEP439: http://www.python.org/dev/peps/pep-0439/


References
==========

.. [#ubuntu] `Ubuntu <http://www.ubuntu.com/>`
.. [#debian] `Debian <http://www.debian.org>`
.. [#fedora] `Fedora <https://fedoraproject.org/>`
.. [#homebrew] `Homebrew  <http://brew.sh/>`
.. [#conda] `Conda <http://www.continuum.io/blog/conda>`


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
