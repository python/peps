Python Enhancement Proposals
============================

The PEPs in this repo are published automatically on the web at
http://www.python.org/dev/peps/.  To learn more about the purpose of
PEPs and how to go about writing a PEP, please start reading at PEP 1
(``pep-0001.txt`` in this repo).  Note that PEP 0, the index PEP, is
now automatically generated, and not committed to the repo.


reStructuredText for PEPs
=========================

Original PEP source may be written using two standard formats, a
mildly idiomatic plaintext format and the reStructuredText format
(also, technically plaintext).  These two formats are described in
PEP 9 and PEP 12 respectively.  The ``pep2html.py`` processing and
installation script knows how to produce the HTML for either PEP
format.

For processing reStructuredText format PEPs, you need the docutils
package, which is available from `PyPI <http://pypi.python.org>`_.
If you have pip, ``pip install docutils`` should install it.


Generating HTML
===============

Do not commit changes with bad formatting.  To check the formatting of
a PEP, use the Makefile.  In particular, to generate HTML for PEP 999,
your source code should be in ``pep-0999.txt`` and the HTML will be
generated to ``pep-0999.html`` by the command ``make pep-0999.html``.
The default Make target generates HTML for all PEPs.  If you don't have
Make, use the ``pep2html.py`` script.


Auto generating the HTML version of Peps from your Pull requests 
================================================================

Once you have forked this repository:

- Enable travis build for your forks:
  - go to https://travis-ci.org/profile/$your_user_name
  - Click `Sync Account`
  - find `$your_username/peps` and enable it.

- Generate a public/private ssh key pair:
  - `$ ssh-keygen -b 2048 -t rsa -f ssh_pair_ghpages_deploy_peps -q -N ""`

- head to `https://travis-ci.org/$your_user_name/peps/settings` and add a hidden environment variable with:
  - the name `DEPLOY_KEY`
  - the content of `$ cat ssh_pair_ghpages_deploy_peps | base64`

- head to `https://github.com/$your_user_name/peps/settings/keys`
  and add a deploy key with the content of `$ cat ssh_pair_ghpages_deploy_peps.pub`


Now every time you push on `$your_username/peps`, a build of the current branch
should be available after a few minutes at
https://yourusername.github.io/peps/${branch-name}/.



