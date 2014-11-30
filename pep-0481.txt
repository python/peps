PEP: 481
Title: Migrate Some Supporting Repositories to Git and Github
Version: $Revision$
Last-Modified: $Date$
Author: Donald Stufft <donald@stufft.io>
Status: Draft
Type: Process
Content-Type: text/x-rst
Created: 29-Nov-2014
Post-History: 29-Nov-2014


Abstract
========

This PEP proposes migrating to Git and Github for certain supporting
repositories (such as the repository for Python Enhancement Proposals) in a way
that is more accessible to new contributors, and easier to manage for core
developers. This is offered as an alternative to PEP 474 which aims to achieve
the same overall benefits but while continuing to use the Mercurial DVCS and
without relying on a commerical entity.

In particular this PEP proposes changes to the following repositories:

* https://hg.python.org/devguide/
* https://hg.python.org/devinabox/
* https://hg.python.org/peps/


This PEP does not propose any changes to the core development workflow for
CPython itself.


Rationale
=========

As PEP 474 mentions, there are currently a number of repositories hosted on
hg.python.org which are not directly used for the development of CPython but
instead are supporting or ancillary repositories. These supporting repositories
do not typically have complex workflows or often branches at all other than the
primary integration branch. This simplicity makes them very good targets for
the "Pull Request" workflow that is commonly found on sites like Github.

However whereas PEP 474 proposes to continue to use Mercurial and restricts
itself to only solutions which are OSS and self-hosted, this PEP expands the
scope of that to include migrating to Git and using Github.

The existing method of contributing to these repositories generally includes
generating a patch and either uploading them to bugs.python.org or emailing
them to peps@python.org. This process is unfriendly towards non-comitter
contributors as well as cumbersome for comitters seeking to accept the patches
sent by users. In contrast, the Pull Request workflow style enables non
techincal contributors, especially those who do not know their way around the
DVCS of choice, to contribute using the web based editor. On the committer
side, the Pull Requests enable them to tell, before merging, whether or not
a particular Pull Request will break anything. It also enables them to do a
simple "push button" merge which does not require them to check out the
changes locally. Another such feature that is useful in particular for docs,
is the ability to view a "prose" diff. This Github-specific feature enables
a committer to view a diff of the rendered output which will hide things like
reformatting a paragraph and show you what the actual "meat" of the change
actually is.


Why Git?
--------

Looking at the variety of DVCS which are available today, it becomes fairly
clear that git has the largest mindshare. The Open Hub (Previously Ohloh)
statistics [#openhub-stats]_ show that currently 37% of the repositories
indexed by Open Hub are using git which is second only to SVN (which has 48%),
while Mercurial has just 2% of the indexed repositories (beating only bazaar
which has 1%). In additon to the Open Hub statistics, a look at the top 100
projects on PyPI (ordered by total download counts) shows that within the
Python space itself, the majority of projects use git.

=== ========= ========== ====== === ====
Git Mercurial Subversion Bazaar CVS None
=== ========= ========== ====== === ====
62  22        7          4      1   1
=== ========= ========== ====== === ====


Chosing a DVCS which has the larger mindshare will make it more likely that any
particular person who has experience with DVCS at all will be able to
meaningfully contribute without having to learn a new tool.

In addition to simply making it more likely that any individual will already
know how to use git, the number of projects and people using it means that the
resources for learning the tool are likely to be more fully fleshed out.
When you run into problems, the liklihood that someone else had that problem
and posted a question and recieved an answer is also far likelier.

Thirdly, by using a more popular tool you also increase your options for
tooling *around* the DVCS itself. Looking at the various options for hosting
repositories, it's extremely rare to find a hosting solution (whether OSS or
commerical) that supports Mercurial but does not support Git. On the flip side,
there are a number of tools which support Git but do not support Mercurial.
Therefore the popularity of git increases the flexibility of our options going
into the future for what toolchain these projects use.

Also, by moving to the more popular DVCS, we increase the likelhood that the
knowledge that the person has learned in contributing to these support
repositories will transfer to projects outside of the immediate CPython project
such as to the larger Python community which is primarily using Git hosted on
Github.

In previous years there was concern about how well supported git was on Windows
in comparison to Mercurial. However, git has grown to support Windows as a
first class citizen. In addition to that, for Windows users who are not well
aquanted with the Windows command line, there are GUI options as well.


Why Github?
-----------

There are a number of software projects or web services which offer
functionality similar to that of Github. These range from commerical web
services such as a Bitbucket to self-hosted OSS solutions such as Kallithea or
Gitlab. This PEP proposes that we move these repositories to Github.

There are two primary reasons for selecting Github: Popularity and
Quality/Polish.

Github is currently the most popular hosted repository hosting according to
Alexa, where it currently has a global rank of 121. Much like for Git itself,
by choosing the most popular tool we gain benefits in increasing the likelhood
that a new contributor will have already experienced the toolchain, the quality
and availablity of the help, more and better tooling being built around it, and
the knowledge transfer to other projects. A look again at the top 100 projects
by download counts on PyPI shows the following hosting locations:

====== ========= =========== ========= =========== ==========
GitHub BitBucket Google Code Launchpad SourceForge Other/Self
====== ========= =========== ========= =========== ==========
62     18        6           4         3           7
====== ========= =========== ========= =========== ==========

In addition to all of those reasons, Github also has the benefit that while
many of the options have similar features when you look at them in a feature
matrix the Github version of each of those features tend to work better and be
far more polished. This is hard to quantify objectively however it is a fairly
common sentiment if you go around and ask people who are using these services
often.

Finally, a reason to choose a web service at all over something that is
self-hosted is to be able to more efficiently use volunteer time and donated
resources. Every additional service hosted on the PSF infrastruture by the
PSF infrastructure team further spreads out the amount of time that the
volunteers on that team have to spend and uses some chunk of resources that
could potentionally be used for something where there is no free or affordable
hosted solution available.

One concern that people do have with using a hosted service is that there is a
lack of control and that at some point in the future the service may no longer
be suitable. It is the opinion of this PEP that Github does not currently and
has not in the past engaged in any attempts to lock people into their platform
and that if at some point in the future Github is no longer suitable for one
reason or another, then at that point we can look at migrating away from Github
onto a different solution. In other words, we'll cross that bridge if and when
we come to it.


Example: Scientific Python
--------------------------

One of the key ideas behind the move to both git and Github is that a feature
of a DVCS, the repository hosting, and the workflow used is the social network
and size of the community using said tools. We can see this is true by looking
at an example from a sub-community of the Python community: The Scientific
Python community. They have already migrated most of the key pieces of the
SciPy stack onto Github using the Pull Request based workflow. This process
started with IPython, and as more projects moved over it became a natural
default for new projects in the community.

They claim to have seen a great benefit from this move, in that it enables
casual contributors to easily move between different projects within their
sub-community without having to learn a special, bespoke workflow and a
different toolchain for each project. They've found that when people can use
their limited time on actually contributing instead of learning the different
tools and workflows that, not only do they contribute more to one project, but
that they also expand out and contribute to other projects. This move has also
been attributed to the increased tendency for members of that community to go
so far as publishing their research and educational materials on Github as
well.

This example showcases the real power behind moving to a highly popular
toolchain and workflow, as each variance introduces yet another hurdle for new
and casual contributors to get past and it makes the time spent learning that
workflow less reusable with other projects.


Migration
=========

Through the use of hg-git [#hg-git]_ we can easily convert a Mercurial
repository to a Git repository by simply pushing the Mercurial repository to
the Git repository. People who wish to continue to use Mercurual locally can
then use hg-git going into the future using the new Github URL. However they
will need to re-clone their repositories as using Git as the server seems to
trigger a one time change of the changeset ids.

As none of the selected repositories have any tags, branches, or bookmarks
other than the ``default`` branch the migration will simply map the ``default``
branch in Mercurial to the ``master`` branch in git.

In addition, since none of the selected projects have any great need of a
complex bug tracker, they will also migrate their issue handling to using the
GitHub issues.

In addition to the migration of the repository hosting itself there are a
number of locations for each particular repository which will require updating.
The bulk of these will simply be changing commands from the hg equivilant to
the git equivilant.

In particular this will include:

* Updating www.python.org to generate PEPs using a git clone and link to
  Github.
* Updating docs.python.org to pull from Github instead of hg.python.org for the
  devguide.
* Enabling the ability to send an email to python-checkins@python.org for each
  push.
* Enabling the ability to send an IRC message to #python-dev on Freenode for
  each push.
* Migrate any issues for these projects to their respective bug tracker on
  Github.
* Use hg-git to provide a read-only mirror on hg.python.org which will enable
  read-only uses of the hg.python.org instances of the specified repositories
  to remain the same.

This will restore these repositories to similar functionality as they currently
have. In addition to this the migration will also include enabling testing for
each pull request using Travis CI [#travisci]_ where possible to ensure that
a new PR does not break the ability to render the documentation or PEPs.


User Access
===========

Moving to Github would involve adding an additional user account that will need
to be managed, however it also offers finer grained control, allowing the
ability to grant someone access to only one particular repository instead of
the coarser grained ACLs available on hg.python.org.


References
==========

.. [#openhub-stats] `Open Hub Statistics <https://www.openhub.net/repositories/compare>`
.. [#hg-git] `hg-git <https://hg-git.github.io/>`
.. [#travisci] `Travis CI <https://travis-ci.org/>`


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
