PEP: <REQUIRED: pep number>
Title: Virtual environment discovery
Author: Brett Cannon <brett@python.org>
Discussions-To: Pending
Status: Draft
Type: Standards Track
Created: 19-Jan-2026
Python-Version: 3.15
Post-History: Pending


Abstract
========

This PEP sets out to help make the discovery of a project's virtual environment
easier for tools by providing a default location as well as a way for a project
to point to its preferred virtual environment when it differs from the default
location.


Motivation
==========

Typically, when someone is working on a project larger than a single file, a
long-lived virtual environment is desirable (the single file case is covered by
:pep:`723` and ephemeral virtual environments). As such, tools working on the
user's behalf may want to create and/or use the same virtual environment. These
tools could be custom scripts in the project like running the test script or
3rd-party tools like package installers.

Unfortunately, there's no guidance on where tools should put a virtual
environment or how to find where one is ultimately put. There's somewhat of a
convention in the community to put a virtual environment locally at the root of
the project in a directory named ``.venv``, but being a convention means it
isn't consistently followed. As well, there is no mechanism to point to a
virtual environment regardless of its location.

This lack of knowing where to find a virtual environment for tools causes the
developer experience to not be as smooth as it could be. If you rely on shell
activation to use the proper virtual environment, then you have to make sure to
do that (either manually or by configuring some automatic shell integration) as
well as to not accidentally reuse that activated shell with another project (or
have set up shell automation to handle the deactivation). Otherwise tools need
to guess or have custom logic per tool that creates virtual environments or ask
users to manually specify where the virtual environment is.

For virtual environment creation, it leads to different instructions per
project on what to do. And those instructions can be critical if scripts and
project configuration rely on the virtual environment being in a certain place.
This can also be an issue when a tool creates a virtual environment
automatically but it isn't obvious where the environment was placed.


Rationale
=========

There are three aspects to where a virtual environment is placed. The first is
whether the virtual environment is local to the project or stored globally with
other virtual environments. Keeping the virtual environment local means that it
is isolated and unique to the project. As well, it means that if you delete the
project you also delete the virtual environment. If you store the virtual
environment globally then you can share it among multiple projects and delete
all virtual environments at once by deleting the directory that contains them
all. Keeping virtual environments global also means it won't be backed up
automatically if a project is stored e.g. in a directory automatically backed
up to remote storage where you pay based on how much storage you use.

Another aspect is the directory name used for the virtual environment
(although this really only affects local virtual environments). If one views
virtual environments as more of a implementation detail, a directory name
starting with ``.`` seemingly makes sense to mark it hidden or de-emphasized
in various tools such as shells and code editors. But hiding it can make
accessing the directory harder by some tools.

Lastly, there's whether you have one virtual environment at a time or many.
Having only one minimizes disk space and keeps it simple by not trying to
manage multiple virtual environments. Having multiple virtual environments,
though, means not having to constantly recreate virtual environments when e.g.
needing to test against multiple python versions.

This PEP takes a two-pronged approach to making virtual environments easily
discoverable while supporting all aspects mentioned above. First, by default,
the virtual environment for the project should be put in the ``.venv``
directory of the project. This name has been chosen due to preexisting tool
support: `Poetry <https://python-poetry.org/docs/configuration#virtualenvsin-project>`__
will detect a virtual environment in such a location,
`PDM <https://pdm-project.org/en/latest/usage/venv/#virtualenv-auto-creation>`__
and `uv <https://docs.astral.sh/uv/concepts/projects/layout/#the-project-environment>`__
create their environments their by default already (
`Hatch can support <https://hatch.pypa.io/latest/blog/2022/10/08/hatch-v160/#virtual-environment-location>`__
a virtual environment there). `VS Code <https://www.jetbrains.com/help/pycharm/creating-virtual-environment.html#env-requirements>`__
will select it automatically while you can configure
`PyCharm <https://www.jetbrains.com/help/pycharm/creating-virtual-environment.html#env-requirements>`__
to use it. The default ``.gitignore`` file for
`GitHub <https://github.com/github/gitignore/blob/main/Python.gitignore>`__,
`GitLab <https://gitlab.com/gitlab-org/gitlab/-/blob/master/vendor/gitignore/Python.gitignore>`__,
XXX codeberg?


Specification
=============

[Describe the syntax and semantics of any new language feature.]


Backwards Compatibility
=======================

[Describe potential impact and severity on pre-existing code.]


Security Implications
=====================

[How could a malicious user take advantage of this new feature?]


How to Teach This
=================

[How to teach users, new and experienced, how to apply the PEP to their work.]


Reference Implementation
========================

[Link to any existing implementation and details about its state, e.g. proof-of-concept.]


Rejected Ideas
==============

[Why certain ideas that were brought while discussing this PEP were not ultimately pursued.]


Open Issues
===========

[Any points that are still being decided/discussed.]


Acknowledgements
================

https://discuss.python.org/t/setting-up-some-guidelines-around-discovering-finding-naming-virtual-environments/22922/

[Thank anyone who has helped with the PEP.]


Footnotes
=========

[A collection of footnotes cited in the PEP, and a place to list non-inline hyperlink targets.]


Copyright
=========

This document is placed in the public domain or under the
CC0-1.0-Universal license, whichever is more permissive.
